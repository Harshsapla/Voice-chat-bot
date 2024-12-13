import express from 'express';
import { SessionsClient } from '@google-cloud/dialogflow'; // Updated import for Dialogflow
import dotenv from 'dotenv';
import cors from 'cors';
import { v4 as uuidv4 } from 'uuid'; // For generating unique session IDs

// Load environment variables from .env file
dotenv.config();

// Check and log the Google Cloud credentials
console.log("Google Cloud Project ID:", process.env.GOOGLE_CLOUD_PROJECT_ID);

// If the project ID or credentials are missing, log an error and stop the server
if (!process.env.GOOGLE_CLOUD_PROJECT_ID || !process.env.GOOGLE_APPLICATION_CREDENTIALS) {
    console.error("ERROR: Google Cloud credentials are missing. Please set them in your .env file.");
    process.exit(1); // Terminate the process if the credentials are missing
}

// Initialize Express app
const app = express();

// Initialize Dialogflow API client with the project ID from the environment variables
const sessionClient = new SessionsClient(); // Use the default credential configuration

// Enable CORS for the frontend (Allow requests from the frontend URL)
app.use(cors({
    origin: process.env.FRONTEND_URL || 'http://localhost:5173', // Default to 'http://localhost:5173' if FRONTEND_URL isn't set
}));

// Middleware to parse JSON request bodies
app.use(express.json());

// API endpoint to handle chat requests
app.post('/api/chat', async (req, res) => {
    const userText = req.body.text; // Extract text input from the frontend request body

    console.log('Received user text:', userText);

    if (!userText || userText.trim().length === 0) {
        return res.status(400).json({ error: "Text input is required and cannot be empty." });
    }

    try {
        // Generate or retrieve a unique session ID for the user (could be from frontend or session storage)
        const sessionId = req.body.sessionId || uuidv4(); // Default to generating a new session ID if not provided

        // Construct a session path using the project ID and the unique session ID
        const sessionPath = sessionClient.projectAgentSessionPath(process.env.GOOGLE_CLOUD_PROJECT_ID, sessionId);

        // Prepare the request for Dialogflow API call
        const request = {
            session: sessionPath,
            query_input: {
                text: {
                    text: userText,
                    language_code: 'en-US',
                },
            },
        };

        // Send the request to Dialogflow and get a response
        const [response] = await sessionClient.detectIntent(request);

        console.log('Dialogflow response:', response);

        // Get the chatbot response from Dialogflow or provide a fallback message if none is returned.
        const chatbotResponse = response.queryResult.fulfillmentText || "Sorry, I couldn't generate a response.";

        console.log('Chatbot response:', chatbotResponse);

        res.json({ response: chatbotResponse });  // Return formatted response

    } catch (error) {
        console.error('Error processing speech request:', error);
        res.status(500).json({ error: error.message || 'An error occurred while processing the request.' });
    }
});

// Start the Express server
const PORT = process.env.PORT || 3000; // Use PORT from environment variable or default to 5000
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

import React, { useEffect, useState } from 'react';

const VoiceSelector = ({ selectedVoice, setSelectedVoice }) => {
    const [voices, setVoices] = useState([]);
    const [isVisible, setIsVisible] = useState(false); // State to control visibility of voice list

    const populateVoiceList = () => {
        const availableVoices = window.speechSynthesis.getVoices();
        setVoices(availableVoices);
    };

    useEffect(() => {
        populateVoiceList();
        window.speechSynthesis.onvoiceschanged = populateVoiceList; // Update voices when they change
    }, []);

    return (
        <div className="voice-selector-container">
            <button className="toggle-voice-button" onClick={() => setIsVisible(!isVisible)}>
                {isVisible ? 'Hide Voices' : 'Show Voices'}
            </button>

            {isVisible && (
                <div className="voice-selector">
                    <div className="voice-list">
                        {voices.map((voice, index) => (
                            <button
                                key={index}
                                className={`voice-button ${selectedVoice === index ? 'active' : ''}`}
                                onClick={() => setSelectedVoice(index)}
                            >
                                {voice.name} ({voice.lang})
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default VoiceSelector;

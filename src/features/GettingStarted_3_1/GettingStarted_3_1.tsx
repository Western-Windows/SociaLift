import { useState } from 'react';
import './GettingStarted_3_1.css';

export interface GettingStarted_3_1Props {
    // Define props here
}

export function GettingStarted_3_1({}: GettingStarted_3_1Props) {
    // State to track which persona is selected (1, 2, or 3). 
    // We set the default to '3' so it looks exactly like your target image on load!
    const [selectedPersona, setSelectedPersona] = useState<number>(3); 

    return (
        <div className="getting-started-container">
            {/* HEADER */}
            <header className="gs-header">
                <button aria-label="Go back" className="gs-back-button" type="button">
                    <span aria-hidden="true">&#8592;</span>
                </button>
                <h1>Getting Started</h1>
            </header>

            <main className="gs-main-layout">
                {/* SIDEBAR */}
                <aside className="gs-sidebar">
                    <div className="gs-step is-complete">
                        <span className="gs-step-check">&#10003;</span>
                        <span className="gs-step-text">Company Information</span>
                    </div>
                    
                    <div className="gs-step is-complete">
                        <span className="gs-step-check">&#10003;</span>
                        <span className="gs-step-text">Products Database</span>
                    </div>
                    
                    <div className="gs-step is-complete">
                        <span className="gs-step-check">&#10003;</span>
                        <span className="gs-step-text">Choose your Persona</span>
                    </div>

                    {/* Dots under Step 3 */}
                    <div className="gs-step-dots">
                        <div className="gs-dot purple-dot"></div>
                        <div className="gs-dot gray-dot"></div>
                    </div>

                    <div className="gs-badge">In progress</div>
                </aside>

                {/* MAIN CONTENT CARD */}
                <section className="gs-form-card">
                    <h2 className="gs-title">Persona Generation</h2>
                    <p className="gs-subtitle">
                        SociaLift provides persona for posts generation.
                    </p>

                    <div className="gs-choices-section">
                        <h3 className="gs-choices-title">Choose Your Persona</h3>

                        <div className="gs-choices-list">
                            {/* Button 1 */}
                            <button 
                                className={`gs-choice ${selectedPersona === 1 ? 'is-selected' : ''}`} 
                                type="button"
                                onClick={() => setSelectedPersona(1)}
                            >
                                The Trusted Curator (Classic & Reliable)
                            </button>

                            {/* Button 2 */}
                            <button 
                                className={`gs-choice ${selectedPersona === 2 ? 'is-selected' : ''}`} 
                                type="button"
                                onClick={() => setSelectedPersona(2)}
                            >
                                The Lifestyle Partner (Warm & Approachable)
                            </button>

                            {/* Button 3 */}
                            <button 
                                className={`gs-choice ${selectedPersona === 3 ? 'is-selected' : ''}`} 
                                type="button"
                                onClick={() => setSelectedPersona(3)}
                            >
                                The Style Authority (Modern & Trend-Forward)
                            </button>
                        </div>
                    </div>

                    <div className="gs-button-row">
                        <button className="gs-continue-button" type="button">
                            Continue &rarr;
                        </button>
                    </div>
                </section>
            </main>
        </div>
    );
}
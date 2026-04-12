import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './GettingStarted_1_1.css';

export interface GettingStarted_1_1Props {}

export function GettingStarted_1_1({}: GettingStarted_1_1Props) {
    const navigate = useNavigate();

    const defaultAboutUs = "e.g: Founded in 1998 by Adelia Malinin, Fashion Hub is a premier multi-brand retailer specializing in high-quality Apparel and Footwear. Our shop features leading brands like Gini and Jony, Catwalk, and Nike. We cater to all age groups and genders, offering everything from casual tops and dresses to athletic footwear and formal shoes, ensuring a complete wardrobe solution for the modern family.";
    const defaultTargetAudience = "Brand-loyal shoppers aged 25 to 55 who prioritize established labels like Nike, Catwalk, and Gini & Jony.";

    const [aboutUs, setAboutUs] = useState('');
    const [targetAudience, setTargetAudience] = useState('');

    const isFormValid = aboutUs.trim() !== '' && targetAudience.trim() !== '';

    return (
        <div className="getting-started-container">
            {/* INJECTED STYLE: This forces the heights and cannot be overridden by external CSS frameworks */}
            <style>{`
                textarea#aboutUs {
                    height: 160px !important;
                    min-height: 160px !important;
                    display: block !important;
                }
                textarea#targetAudience {
                    height: 100px !important;
                    min-height: 100px !important;
                    display: block !important;
                }
            `}</style>

            <header className="gs-header">
                <button aria-label="Go back" className="gs-back-button" type="button" onClick={() => navigate(-1)}>
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

                    <div className="gs-step-dots">
                        <div className="gs-dot purple-dot"></div>
                        <div className="gs-dot gray-dot"></div>
                    </div>
                    
                    <div className="gs-step">
                        <span className="gs-step-num idle-num">2</span>
                        <span className="gs-step-text">Products Database</span>
                    </div>
                    
                    <div className="gs-step">
                        <span className="gs-step-num idle-num">3</span>
                        <span className="gs-step-text">Choose your Persona</span>
                    </div>

                    <div className="gs-badge">In progress</div>
                </aside>

                {/* MAIN CONTENT CARD */}
                <section className="gs-form-card">
                    <h2 className="gs-title">Company Information</h2>
                    <p className="gs-subtitle">
                        SociaLift collects this information to better understand and serve your business.
                    </p>

                    <form className="gs-form-wrapper">
                        {/* About Us Field */}
                        <div className="gs-input-group">
                            <label htmlFor="aboutUs" className="gs-label-title">About Us</label>
                            <textarea
                                id="aboutUs"
                                name="aboutUs"
                                className="gs-textarea"
                                value={aboutUs}
                                onChange={(e) => setAboutUs(e.target.value)}
                                placeholder={defaultAboutUs}
                            />
                        </div>

                        {/* Target Audience Field */}
                        <div className="gs-input-group" style={{ marginTop: '1.5rem' }}>
                            <label htmlFor="targetAudience" className="gs-label-title">Target Audience</label>
                            <textarea
                                id="targetAudience"
                                name="targetAudience"
                                className="gs-textarea"
                                value={targetAudience}
                                onChange={(e) => setTargetAudience(e.target.value)}
                                placeholder={defaultTargetAudience}
                            />
                        </div>

                        <div className="gs-button-row">
                            <button 
                                className="gs-continue-button" 
                                type="button" 
                                onClick={() => navigate('/getting-started/1-2')}
                                disabled={!isFormValid}
                                style={{ opacity: isFormValid ? 1 : 0.5, cursor: isFormValid ? 'pointer' : 'not-allowed' }}
                            >
                                Continue &rarr;
                            </button>
                        </div>
                    </form>
                </section>
            </main>
        </div>
    );
}
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './GettingStarted_3_0.css';

export interface GettingStarted_3_0Props {}

export function GettingStarted_3_0({}: GettingStarted_3_0Props) {
    const navigate = useNavigate();
    
    const defaultSampleText = `e.g.: From the playground to the boardroom, and every workout in between—Fashion Hub has been your family's style partner since 1998. Whether you're hunting for the latest Nike kicks, a sharp pair of Catwalk heels, or durable, trend-setting outfits from Gini & Jony for the little ones, we've curated the best brands.\n\n✨ What's in store?\n• For Her: Elegant dresses and formal footwear.\n• For Him: Casual tops and performance athletic gear.\n• For Kids: High-quality apparel built for play.\n\nUpgrade the whole family's wardrobe today. Quality isn't just a promise; it's our heritage.\n📍 Visit us in-store or DM for personal styling assistance!\n#FashionHub #FamilyStyle #Nike #Catwalk #GiniAndJony #ModernWardrobe #QualityFashion`;
    
    // Initialize state as an empty string
    const [postText, setPostText] = useState('');

    // Validation: Ensure post box has content typed by the user
    const isFormValid = postText.trim() !== '';

    return (
        <div className="getting-started-container">
            <header className="gs-header">
                <button aria-label="Go back" className="gs-back-button" type="button" onClick={() => navigate(-1)}><span aria-hidden="true">&#8592;</span></button>
                <h1>Getting Started</h1>
            </header>

            <main className="gs-main-layout">
                {/* SIDEBAR */}
                <aside className="gs-sidebar">
                    <div className="gs-step is-complete"><span className="gs-step-check">&#10003;</span><span className="gs-step-text">Company Information</span></div>
                    <div className="gs-step is-complete"><span className="gs-step-check">&#10003;</span><span className="gs-step-text">Products Database</span></div>
                    <div className="gs-step is-active"><span className="gs-step-num">3</span><span className="gs-step-text">Choose your Persona</span></div>
                    <div className="gs-step-dots"><div className="gs-dot gray-dot"></div><div className="gs-dot gray-dot"></div></div>
                    <div className="gs-badge">In progress</div>
                </aside>

                <section className="gs-form-card">
                    <h2 className="gs-title">Persona Generation</h2>
                    <p className="gs-subtitle">SociaLift provides persona for posts generation.</p>

                    <form className="gs-form-wrapper">
                        <div className="gs-input-group">
                            <label htmlFor="samplePost" className="gs-label-title">Sample Post</label>
                            <span className="gs-label-help">We need you to write a post to get to know your persona / voice better.</span>
                            
                            {/* Pass default text to the placeholder attribute */}
                            <textarea
                                id="samplePost"
                                name="samplePost"
                                className="gs-textarea"
                                value={postText}
                                onChange={(e) => setPostText(e.target.value)}
                                rows={11}
                                placeholder={defaultSampleText}
                            />
                        </div>

                        <div className="gs-button-row">
                            <button 
                                className="gs-continue-button" 
                                type="button" 
                                onClick={() => navigate('/getting-started/3-1')}
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
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './GettingStarted_1_0.css';

export interface GettingStarted_1_0Props {}

export function GettingStarted_1_0({}: GettingStarted_1_0Props) {
    const navigate = useNavigate();

    // 1. State to track form inputs
    const [formData, setFormData] = useState({
        companyName: '',
        founderName: '',
        hotline: '',
        phoneNumber: '',
        emailAddress: ''
    });

    // 2. State to track which fields the user has interacted with
    const [touched, setTouched] = useState({
        hotline: false,
        phoneNumber: false,
        emailAddress: false
    });

    // 3. Handlers
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
        const { name } = e.target;
        setTouched(prev => ({ ...prev, [name]: true }));
    };

    // 4. Validation Regex Patterns
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    // Supports typical mobile structures (e.g., 11 digits) with optional +, spaces, or dashes
    const phoneRegex = /^\+?[\d\s\-]{8,15}$/; 
    
    // Supports shorter commercial hotlines (e.g., 5-digit numbers) up to standard lengths
    const hotlineRegex = /^[\d\s\-]{3,10}$/;

    // 5. Validity Checks
    const isEmailValid = emailRegex.test(formData.emailAddress);
    const isPhoneValid = phoneRegex.test(formData.phoneNumber);
    const isHotlineValid = hotlineRegex.test(formData.hotline);
    const isCompanyValid = formData.companyName.trim() !== '';
    const isFounderValid = formData.founderName.trim() !== '';

    // 6. Overall form validation check
    const isFormValid = isEmailValid && isPhoneValid && isHotlineValid && isCompanyValid && isFounderValid;

    // Helper style for inline error messages
    const errorStyle = { color: '#e74c3c', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' };

    return (
        <div className="getting-started-container">
            <header className="gs-header">
                <button aria-label="Go back" className="gs-back-button" type="button" onClick={() => navigate(-1)}>
                    <span aria-hidden="true">&#8592;</span>
                </button>
                <h1>Getting Started</h1>
            </header>

            <main className="gs-main-layout">
                {/* SIDEBAR */}
                <aside className="gs-sidebar">
                    <div className="gs-step is-active">
                        <span className="gs-step-num">1</span>
                        <span className="gs-step-text">Company Information</span>
                    </div>
                    <div className="gs-step-dots">
                        <div className="gs-dot"></div>
                        <div className="gs-dot"></div>
                    </div>
                    <div className="gs-step">
                        <span className="gs-step-num">2</span>
                        <span className="gs-step-text">Products Database</span>
                    </div>
                    <div className="gs-step">
                        <span className="gs-step-num">3</span>
                        <span className="gs-step-text">Choose your Persona</span>
                    </div>
                    <div className="gs-badge">In progress</div>
                </aside>

                {/* FORM AREA */}
                <section className="gs-form-card">
                    <h2 className="gs-title">Company Information</h2>
                    <p className="gs-subtitle">
                        SociaLift collects this information to better understand and serve your business.
                    </p>

                    <form className="gs-form-grid">
                        <div className="gs-input-group">
                            <label htmlFor="companyName">Company Name</label>
                            <input id="companyName" name="companyName" placeholder="Company Name" type="text" value={formData.companyName} onChange={handleChange} />
                        </div>

                        <div className="gs-input-group">
                            <label htmlFor="founderName">Founder Name</label>
                            <input id="founderName" name="founderName" placeholder="Founder Name" type="text" value={formData.founderName} onChange={handleChange} />
                        </div>

                        <div className="gs-input-group">
                            <label htmlFor="hotline">Hotline</label>
                            <input 
                                id="hotline" 
                                name="hotline" 
                                placeholder="e.g. 19000 or standard number" 
                                type="tel" 
                                value={formData.hotline} 
                                onChange={handleChange} 
                                onBlur={handleBlur}
                            />
                            {touched.hotline && !isHotlineValid && formData.hotline !== '' && (
                                <span style={errorStyle}>Please enter a valid hotline number.</span>
                            )}
                        </div>

                        <div className="gs-input-group">
                            <label htmlFor="phoneNumber">Phone Number</label>
                            <input 
                                id="phoneNumber" 
                                name="phoneNumber" 
                                placeholder="Phone Number" 
                                type="tel" 
                                value={formData.phoneNumber} 
                                onChange={handleChange}
                                onBlur={handleBlur} 
                            />
                            {touched.phoneNumber && !isPhoneValid && formData.phoneNumber !== '' && (
                                <span style={errorStyle}>Please enter a valid phone number.</span>
                            )}
                        </div>

                        <div className="gs-input-group">
                            <label htmlFor="emailAddress">Email Address</label>
                            <input 
                                id="emailAddress" 
                                name="emailAddress" 
                                placeholder="Email Address" 
                                type="email" 
                                value={formData.emailAddress} 
                                onChange={handleChange}
                                onBlur={handleBlur} 
                            />
                            {touched.emailAddress && !isEmailValid && formData.emailAddress !== '' && (
                                <span style={errorStyle}>Please enter a valid email address.</span>
                            )}
                        </div>

                        <div className="gs-button-row">
                            <button 
                                className="gs-submit-btn" 
                                type="button" 
                                onClick={() => navigate('/getting-started/1-1')}
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
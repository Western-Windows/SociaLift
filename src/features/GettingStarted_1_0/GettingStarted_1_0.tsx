import './GettingStarted_1_0.css';

export interface GettingStarted_1_0Props {
    // Define props here
}

export function GettingStarted_1_0({}: GettingStarted_1_0Props) {
    return (
        <div className="getting-started-container">
            {/* GRADIENT HEADER */}
            <header className="gs-header">
                <button aria-label="Go back" className="gs-back-button" type="button">
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
                            <input id="companyName" name="companyName" placeholder="Company Name" type="text" />
                        </div>

                        <div className="gs-input-group">
                            <label htmlFor="founderName">Founder Name</label>
                            <input id="founderName" name="founderName" placeholder="Founder Name" type="text" />
                        </div>

                        <div className="gs-input-group">
                            <label htmlFor="hotline">Hotline</label>
                            <input id="hotline" name="hotline" placeholder="Hotline" type="tel" />
                        </div>

                        <div className="gs-input-group">
                            <label htmlFor="phoneNumber">Phone Number</label>
                            <input id="phoneNumber" name="phoneNumber" placeholder="Phone Number" type="tel" />
                        </div>

                        <div className="gs-input-group">
                            <label htmlFor="emailAddress">Email Address</label>
                            <input id="emailAddress" name="emailAddress" placeholder="Email Address" type="email" />
                        </div>

                        <div className="gs-button-row">
                            <button className="gs-submit-btn" type="button">
                                Continue &rarr;
                            </button>
                        </div>
                    </form>
                </section>
            </main>
        </div>
    );
}
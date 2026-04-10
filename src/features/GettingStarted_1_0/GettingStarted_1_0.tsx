import './GettingStarted_1_0.css';

export interface GettingStarted_1_0Props {
    // Define props here
}

export function GettingStarted_1_0({}: GettingStarted_1_0Props) {
    return (
        <div className="getting-started-1-0" data-node-id="162:2086">
            <header className="gs-header">
                <button aria-label="Go back" className="gs-back-button" type="button">
                    <span aria-hidden="true">&#8592;</span>
                </button>
                <h1>Getting Started</h1>
            </header>

            <main className="gs-main">
                <aside className="gs-steps" aria-label="Onboarding progress">
                    <ol>
                        <li className="is-active">
                            <span className="gs-step-index">1</span>
                            <span className="gs-step-label">Company Information</span>
                        </li>
                        <div className="gs-step-dots">
                            <span className="gs-dot"></span>
                            <span className="gs-dot"></span>
                        </div>
                        <li>
                            <span className="gs-step-index">2</span>
                            <span className="gs-step-label">Products Database</span>
                        </li>
                        <li>
                            <span className="gs-step-index">3</span>
                            <span className="gs-step-label">Choose your Persona</span>
                        </li>
                    </ol>
                    <span className="gs-step-badge">In progress</span>
                </aside>

                <section className="gs-form-shell" aria-labelledby="company-info-title">
                    <h2 id="company-info-title">Company Information</h2>
                    <p>
                        SociaLift collects this information to better understand and serve your
                        business.
                    </p>

                    <form className="gs-form-grid">
                        <label>
                            <span>Company Name</span>
                            <input name="companyName" placeholder="Company Name" type="text" />
                        </label>

                        <label>
                            <span>Founder Name</span>
                            <input name="founderName" placeholder="Founder Name" type="text" />
                        </label>

                        <label>
                            <span>Hotline</span>
                            <input name="hotline" placeholder="Hotline" type="tel" />
                        </label>

                        <label>
                            <span>Phone Number</span>
                            <input name="phoneNumber" placeholder="Phone Number" type="tel" />
                        </label>

                        {/* Email address now spans only one column natively in the grid */}
                        <label>
                            <span>Email Address</span>
                            <input name="emailAddress" placeholder="Email Address" type="email" />
                        </label>

                        <div className="gs-submit-row">
                            <button className="gs-continue-button" type="button">
                                Continue <span aria-hidden="true">&#8594;</span>
                            </button>
                        </div>
                    </form>
                </section>
            </main>
        </div>
    );
}
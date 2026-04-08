import './GettingStarted_1_2.css';

// 1. Automatically scaffold the TypeScript interface
export interface GettingStarted_1_2Props {
    // Define props here
}

// 2. Clean, compiler-friendly functional component
export function GettingStarted_1_2({}: GettingStarted_1_2Props) {
    return (
        <div className="getting-started-1-2" data-node-id="162:2185">
            <header className="gs-header">
                <button aria-label="Go back" className="gs-back-button" type="button">
                    <span aria-hidden="true">&#8592;</span>
                </button>
                <h1>Getting Started</h1>
            </header>

            <main className="gs-main">
                <aside className="gs-steps" aria-label="Onboarding progress">
                    <ol>
                        <li className="is-complete">
                            <span className="gs-step-index gs-step-check" aria-hidden="true">
                                &#10003;
                            </span>
                            <span className="gs-step-label">Company Information</span>
                        </li>
                        <li className="is-current">
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

                    <form className="gs-form-grid gs-products-grid">
                        <div className="gs-field-row">
                            <label className="gs-field-group">
                                <span>Services</span>
                                <div className="gs-input-with-addon">
                                    <input name="services" placeholder="Services" type="text" />
                                    <button aria-label="Add service" className="gs-add-button" type="button">
                                        <span aria-hidden="true">+</span>
                                    </button>
                                </div>
                            </label>
                        </div>

                        <div className="gs-field-row">
                            <label className="gs-field-group">
                                <span>Store Locations</span>
                                <div className="gs-input-with-addon">
                                    <input name="storeLocations" placeholder="Store Locations" type="text" />
                                    <button aria-label="Add store location" className="gs-add-button" type="button">
                                        <span aria-hidden="true">+</span>
                                    </button>
                                </div>
                            </label>
                        </div>

                        <button className="gs-continue-button" type="button">
                            Continue <span aria-hidden="true">&#8594;</span>
                        </button>
                    </form>
                </section>
            </main>
        </div>
    );
}
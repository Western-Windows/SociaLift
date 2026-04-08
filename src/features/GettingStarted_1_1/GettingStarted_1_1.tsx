import './GettingStarted_1_1.css';

// 1. Automatically scaffold the TypeScript interface
export interface GettingStarted_1_1Props {
    // Define props here
}

// 2. Clean, compiler-friendly functional component
export function GettingStarted_1_1({}: GettingStarted_1_1Props) {
    return (
        <div className="getting-started-1-1" data-node-id="162:2140">
            <header className="gs-header">
                <button aria-label="Go back" className="gs-back-button" type="button">
                    <span aria-hidden="true">&#8592;</span>
                </button>
                <h1>Getting Started</h1>
            </header>

            <main className="gs-main">
                <aside className="gs-steps" aria-label="Onboarding progress">
                    <ol>
                        <li className="is-complete is-active">
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

                    <form className="gs-form-grid">
                        <label className="gs-full-width">
                            <span>About Us</span>
                            <textarea
                                defaultValue={
                                    'e.g: Founded in 1998 by Adelia Malinin, Fashion Hub is a premier multi-brand retailer specializing in high-quality Apparel and Footwear. Our shop features leading brands like Gini and Jony, Catwalk, and Nike. We cater to all age groups and genders, offering everything from casual tops and dresses to athletic footwear and formal shoes, ensuring a complete wardrobe solution for the modern family.'
                                }
                                name="aboutUs"
                                rows={5}
                            />
                        </label>

                        <label className="gs-full-width">
                            <span>Target Audience</span>
                            <textarea
                                defaultValue="Brand-loyal shoppers aged 25 to 55 who prioritize established labels like Nike, Catwalk, and Gini & Jony."
                                name="targetAudience"
                                rows={3}
                            />
                        </label>

                        <button className="gs-continue-button" type="button">
                            Continue <span aria-hidden="true">&#8594;</span>
                        </button>
                    </form>
                </section>
            </main>
        </div>
    );
}
import './GettingStarted_3_1.css';

// 1. Automatically scaffold the TypeScript interface
export interface GettingStarted_3_1Props {
    // Define props here
}

// 2. Clean, compiler-friendly functional component
export function GettingStarted_3_1({}: GettingStarted_3_1Props) {
    return (
        <div className="getting-started-3-1" data-node-id="162:2319">
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
                        <li className="is-complete">
                            <span className="gs-step-index gs-step-check" aria-hidden="true">
                                &#10003;
                            </span>
                            <span className="gs-step-label">Products Database</span>
                        </li>
                        <li className="is-complete">
                            <span className="gs-step-index gs-step-check" aria-hidden="true">
                                &#10003;
                            </span>
                            <span className="gs-step-label">Choose your Persona</span>
                        </li>
                    </ol>
                    <span className="gs-step-badge">In progress</span>
                </aside>

                <section className="gs-form-shell" aria-labelledby="persona-title">
                    <h2 id="persona-title">Persona Generation</h2>
                    <p>SociaLift provides persona for posts generation.</p>

                    <div className="gs-choices">
                        <h3>Choose Your Persona</h3>

                        <button className="gs-choice gs-choice-soft" type="button">
                            The Trusted Curator (Classic &amp; Reliable)
                        </button>

                        <button className="gs-choice" type="button">
                            The Lifestyle Partner (Warm &amp; Approachable)
                        </button>

                        <button className="gs-choice gs-choice-strong" type="button">
                            The Style Authority (Modern &amp; Trend-Forward)
                        </button>
                    </div>

                    <button className="gs-continue-button" type="button">
                        Continue <span aria-hidden="true">&#8594;</span>
                    </button>
                </section>
            </main>
        </div>
    );
}
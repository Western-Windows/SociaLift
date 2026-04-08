import './GettingStarted_2_0.css';

// 1. Automatically scaffold the TypeScript interface
export interface GettingStarted_2_0Props {
    // Define props here
}

// 2. Clean, compiler-friendly functional component
export function GettingStarted_2_0({}: GettingStarted_2_0Props) {
    return (
        <div className="getting-started-2-0" data-node-id="162:2363">
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

                <section className="gs-form-shell" aria-labelledby="product-db-title">
                    <h2 id="product-db-title">Product Database</h2>
                    <p>
                        SociaLift collects this information to better understand and serve your
                        business.
                    </p>

                    <form className="gs-form-grid">
                        <label className="gs-full-width">
                            <span>Products</span>

                            <div className="gs-upload-surface">
                                <div className="gs-upload-dashed">
                                    <div className="gs-upload-icon" aria-hidden="true">
                                        <span className="gs-upload-arrow" />
                                    </div>
                                    <p>Drag and drop files here, or click to browse</p>
                                    <button className="gs-browse-button" type="button">
                                        Browse Files
                                    </button>
                                </div>
                            </div>
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
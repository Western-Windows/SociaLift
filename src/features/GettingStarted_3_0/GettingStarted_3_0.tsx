import './GettingStarted_3_0.css';

// 1. Automatically scaffold the TypeScript interface
export interface GettingStarted_3_0Props {
    // Define props here
}

// 2. Clean, compiler-friendly functional component
export function GettingStarted_3_0({}: GettingStarted_3_0Props) {
    return (
        <div className="getting-started-3-0" data-node-id="162:2236">
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
                        <li className="is-current">
                            <span className="gs-step-index">3</span>
                            <span className="gs-step-label">Choose your Persona</span>
                        </li>
                    </ol>
                    <span className="gs-step-badge">In progress</span>
                </aside>

                <section className="gs-form-shell" aria-labelledby="persona-title">
                    <h2 id="persona-title">Persona Generation</h2>
                    <p>SociaLift provides persona for posts generation.</p>

                    <form className="gs-form-grid">
                        <label className="gs-full-width">
                            <span>Sample Post</span>
                            <span className="gs-field-help">
                                We need you to write a post to get to know your persona / voice
                                better.
                            </span>
                            <textarea
                                defaultValue={
                                    'e.g.: From the playground to the boardroom, and every workout in between-Fashion Hub has been your family\'s style partner since 1998. Whether you\'re hunting for the latest Nike kicks, a sharp pair of Catwalk heels, or durable, trend-setting outfits from Gini & Jony for the little ones, we\'ve curated the best brands.\n\n✨ What\'s in store?\n• For Her: Elegant dresses and formal footwear.\n• For Him: Casual tops and performance athletic gear.\n• For Kids: High-quality apparel built for play.\n\nUpgrade the whole family\'s wardrobe today. Quality isn\'t just a promise; it\'s our heritage.\n📍 Visit us in-store or DM for personal styling assistance!\n#FashionHub #FamilyStyle #Nike #Catwalk #GiniAndJony #ModernWardrobe #QualityFashion'
                                }
                                name="samplePost"
                                rows={11}
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
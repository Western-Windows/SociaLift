import { useState } from 'react';
import './GettingStarted_1_2.css';

export interface GettingStarted_1_2Props {
    // Define props here
}

export function GettingStarted_1_2({}: GettingStarted_1_2Props) {
    // State arrays to hold the list of input values. Initialize with one empty string.
    const [services, setServices] = useState<string[]>(['']);
    const [locations, setLocations] = useState<string[]>(['']);

    // --- Handlers for Services ---
    const handleServiceChange = (index: number, value: string) => {
        const newServices = [...services];
        newServices[index] = value;
        setServices(newServices);
    };

    const addServiceField = () => {
        setServices([...services, '']);
    };

    // --- Handlers for Store Locations ---
    const handleLocationChange = (index: number, value: string) => {
        const newLocations = [...locations];
        newLocations[index] = value;
        setLocations(newLocations);
    };

    const addLocationField = () => {
        setLocations([...locations, '']);
    };

    return (
        <div className="getting-started-container">
            {/* HEADER */}
            <header className="gs-header">
                <button aria-label="Go back" className="gs-back-button" type="button">
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
                        <div className="gs-dot green-dot"></div>
                        <div className="gs-dot purple-dot"></div>
                    </div>
                    
                    <div className="gs-step is-active">
                        <span className="gs-step-num">2</span>
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
                        
                        {/* 2-Column Grid Area */}
                        <div className="gs-form-grid">
                            
                            {/* LEFT COLUMN: Services */}
                            <div className="gs-field-column">
                                <label className="gs-col-title">Services</label>
                                <div className="gs-dynamic-list">
                                    {services.map((service, index) => (
                                        <div className="gs-input-with-addon" key={`service-${index}`}>
                                            <input 
                                                placeholder="Services" 
                                                type="text" 
                                                value={service}
                                                onChange={(e) => handleServiceChange(index, e.target.value)}
                                            />
                                            {/* Only show the + button on the LAST input */}
                                            {index === services.length - 1 ? (
                                                <button 
                                                    aria-label="Add service" 
                                                    className="gs-add-button" 
                                                    type="button"
                                                    onClick={addServiceField}
                                                >
                                                    <span aria-hidden="true">+</span>
                                                </button>
                                            ) : (
                                                // Invisible placeholder to keep inputs aligned when there is no button
                                                <div className="gs-add-button-placeholder"></div> 
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* RIGHT COLUMN: Store Locations */}
                            <div className="gs-field-column">
                                <label className="gs-col-title">Store Locations</label>
                                <div className="gs-dynamic-list">
                                    {locations.map((location, index) => (
                                        <div className="gs-input-with-addon" key={`location-${index}`}>
                                            <input 
                                                placeholder="Store Locations" 
                                                type="text" 
                                                value={location}
                                                onChange={(e) => handleLocationChange(index, e.target.value)}
                                            />
                                            {/* Only show the + button on the LAST input */}
                                            {index === locations.length - 1 ? (
                                                <button 
                                                    aria-label="Add store location" 
                                                    className="gs-add-button" 
                                                    type="button"
                                                    onClick={addLocationField}
                                                >
                                                    <span aria-hidden="true">+</span>
                                                </button>
                                            ) : (
                                                <div className="gs-add-button-placeholder"></div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>

                        </div>

                        <div className="gs-button-row">
                            <button className="gs-continue-button" type="button">
                                Continue &rarr;
                            </button>
                        </div>
                    </form>
                </section>
            </main>
        </div>
    );
}
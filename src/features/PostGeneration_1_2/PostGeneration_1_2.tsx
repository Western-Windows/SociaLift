import { useNavigate } from 'react-router-dom';
import './PostGeneration_1_2.css';

export interface PostGeneration_1_2Props {
    // Define props here
}

export function PostGeneration_1_2({}: PostGeneration_1_2Props) {
    const navigate = useNavigate();

    return (
        <div className="getting-started-container">

            <main className="gs-main-layout">
      <div className="post-generation-container">
      <main className="pg-main-layout">
        
        {/* SIDEBAR */}
        <aside className="pg-sidebar">
          {/* Step 1: Completed */}
          <div className="pg-step">
            <span className="pg-step-check">&#10003;</span>
            <span className="pg-step-text pg-completed-text">Generate Post</span>
          </div>

          {/* Thick vertical line (Teal to show progress) */}
          <div className="pg-step-line pg-line-completed"></div>

          {/* Step 2: Active */}
          <div className="pg-step">
            <span className="pg-step-num pg-active-num">2</span>
            <span className="pg-step-text pg-active-text">See post</span>
          </div>

          <div className="pg-badge">In progress</div>
        </aside>

        {/* MAIN CONTENT CARD */}
        <section className="pg-form-card">
          <h2 className="pg-title">You chose to have 'Edit & Approve' privileges, here is your post, tune it to your liking!</h2>
          <p className="pg-subtitle-link">Edit by selecting the text below.</p>

          <form className="pg-form-wrapper" onSubmit={(e) => e.preventDefault()}>
            
            {/* Editable Text Area */}
            <div className="pg-input-group">
              <textarea
                className="pg-textarea-editable"
                value={`Exciting news! Our latest product is now available. Check it out and let us know what you think! #NewProduct #Innovation`}
                readOnly
                rows={12}
              />
            </div>

            {/* Action Area (Buttons & Note) */}
            <div className="pg-action-area">
              <div className="pg-button-row">
                
                {/* Schedule Button */}
                <button className="pg-submit-btn pg-btn-primary" type="button">
                    Approve & Schedule Post
                  <svg 
                    width="18" 
                    height="18" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2" 
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                  </svg>
                </button>
                
                {/* Primary Action Button */}
                <button className="pg-submit-btn pg-btn-primary" type="button">
                  Approve & Post Now &rarr;
                </button>
                
              </div>
              
              <div className="pg-info-note">
                <svg className="pg-info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                  <line x1="12" y1="9" x2="12" y2="13"></line>
                  <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                The post will be scheduled at the best time with the highest reach and engagement
              </div>
            </div>
            
          </form>
        </section>
      </main>
    </div>
                {/* OVERLAY & MODAL (Rendered inside main layout so it sits under the header) */}
                <div className="gs-overlay" aria-hidden="true" />

                <section className="gs-success-modal" aria-label="Success confirmation">
                    <div className="gs-success-icon" aria-hidden="true">
                        &#10003;
                    </div>
                    <h3>SUCCESS!</h3>
                    <p>
                        To view or modify the posted post, 
                        please navigate to Facebook.
                    </p>
                    <button className="gs-success-continue" type="button" onClick={() => navigate('/dashboard')}>
                        Continue
                    </button>
                </section>
            </main>
        </div>
    );
}
import './PostGeneration_1_1A.css';
import { useNavigate } from 'react-router-dom'; // 1. Import useNavigate
export interface PostGeneration_1_1AProps {
  // Define props here
}

export function PostGeneration_1_1A({}: PostGeneration_1_1AProps) {
  const navigate = useNavigate(); // 2. Initialize the navigate function
  const samplePostContent = `e.g.: From the playground to the boardroom, and every workout in between—Fashion Hub has been your family's style partner since 1998. Whether you're hunting for the latest Nike kicks, a sharp pair of Catwalk heels, or durable, trend-setting outfits from Gini & Jony for the little ones, we've curated the best brands.\n✨ What's in store?\n• For Her: Elegant dresses and formal footwear.\n• For Him: Casual tops and performance athletic gear.\n• For Kids: High-quality apparel built for play.\nUpgrade the whole family's wardrobe today. Quality isn't just a promise; it's our heritage.\n📍 Visit us in-store or DM for personal styling assistance!\n#FashionHub #FamilyStyle #Nike #Catwalk #GiniAndJony #ModernWardrobe #QualityFashion`;

  return (
    <div className="post-generation-container">
      <main className="pg-main-layout">
        
        <aside className="pg-sidebar">
          {/* 3. Add onClick and the pg-step-clickable class */}
          <div 
            className="pg-step pg-step-clickable" 
            onClick={() => navigate(-1)} /* navigate(-1) takes them exactly one page back */
          >
            <span className="pg-step-check">&#10003;</span>
            <span className="pg-step-text pg-completed-text">Generate Post</span>
          </div>

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
          <h2 className="pg-title">You chose to have 'View Only' privileges, here is your post!</h2>

          <form className="pg-form-wrapper" onSubmit={(e) => e.preventDefault()}>
            
            {/* View-Only Text Area */}
            <div className="pg-input-group">
              <textarea
                className="pg-textarea-readonly"
                readOnly
                value={samplePostContent}
                rows={12}
              />
            </div>

            {/* Action Area (Buttons & Note) */}
            <div className="pg-action-area">
              <div className="pg-button-row">
                
                {/* Schedule Button (Now identical to Primary) */}
                <button className="pg-submit-btn pg-btn-primary" type="button" onClick={() => navigate('/post-gen1-2')}>
                    Schedule Post
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
                
                {/* Post Now Button */}
                <button className="pg-submit-btn pg-btn-primary" type="button" onClick={() => navigate('/post-gen1-2')}>
                  Post Now &rarr;
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
  );
}
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './PostGeneration.css';

export interface PostGenerationProps {
  // Define props here if needed
}

export function PostGeneration({}: PostGenerationProps) {
  const navigate = useNavigate();

  // --- Flow State ---
  // 1: Generate Post (Input), 2: See Post (View/Edit), 3: Success Modal
  const [currentStep, setCurrentStep] = useState<1 | 2 | 3>(1);

  // --- Step 1 State ---
  const [generationMode, setGenerationMode] = useState('sample');
  const [requireApproval, setRequireApproval] = useState(true);
  const [inputText, setInputText] = useState('');

  // --- Step 2 State ---
  const [generatedText, setGeneratedText] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isScheduling, setIsScheduling] = useState(false);



  // --- Handlers ---
  const handleGeneratePost = async () => {
    const userId = localStorage.getItem('socialift_user_id');
    if (!userId) {
      alert("Please log in first.");
      return;
    }

    setIsGenerating(true);
    try {
      const response = await fetch("http://localhost:8000/api/posts/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: parseInt(userId, 10),
          message: inputText,
          input_type: generationMode === 'sample' ? 'post' : 'idea'
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate post");
      }

      const data = await response.json();
      setGeneratedText(data.generated_post);
      setCurrentStep(2);
    } catch (error) {
      console.error(error);
      alert("Error generating post. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePostAction = async (mode: 'schedule' | 'now') => {
    const userId = localStorage.getItem('socialift_user_id');
    if (!userId) {
      alert("Please log in first.");
      return;
    }

    setIsScheduling(true);
    try {
      const response = await fetch("http://localhost:8000/api/posts/schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: parseInt(userId, 10),
          message: generatedText,
          input_type: generationMode === 'sample' ? 'post' : 'idea',
          scheduled_time_str: mode === 'now' ? 'now' : 'auto',
          skip_enhancement: true
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to schedule/post");
      }

      // Triggers the Success Modal overlay
      setCurrentStep(3);
    } catch (error) {
      console.error(error);
      alert(`Error ${mode === 'now' ? 'posting' : 'scheduling'}. Please try again.`);
    } finally {
      setIsScheduling(false);
    }
  };

  return (
    <div className="post-generation-container">
      <main className="pg-main-layout">
        
        {/* SIDEBAR */}
        <aside className="pg-sidebar">
          {/* Step 1 Indicator */}
          <div 
            className={`pg-step ${currentStep > 1 ? 'pg-step-clickable' : ''}`} 
            onClick={() => currentStep > 1 && setCurrentStep(1)}
          >
            {currentStep > 1 ? (
              <span className="pg-step-check">&#10003;</span>
            ) : (
              <span className="pg-step-num pg-active-num">1</span>
            )}
            <span className={`pg-step-text ${currentStep > 1 ? 'pg-completed-text' : 'pg-active-text'}`}>
              Generate Post
            </span>
          </div>

          <div className={`pg-step-line ${currentStep > 1 ? 'pg-line-completed' : ''}`}></div>

          {/* Step 2 Indicator */}
          <div className="pg-step">
            <span className={`pg-step-num ${currentStep > 1 ? 'pg-active-num' : 'pg-idle-num'}`}>2</span>
            <span className={`pg-step-text ${currentStep > 1 ? 'pg-active-text' : ''}`}>See post</span>
          </div>

          <div className="pg-badge">In progress</div>
        </aside>

        {/* MAIN CONTENT CARD */}
        <section className="pg-form-card">
          {currentStep === 1 ? (
            /* --- STEP 1: GENERATE POST FORM --- */
            <>
              <h2 className="pg-title">How would you like to generate this new post?</h2>
              <p className="pg-subtitle">
                You may provide a sample post for us to follow, or you can leave the creative direction to us and simply provide the topic.
              </p>

              <form className="pg-form-wrapper" onSubmit={(e) => e.preventDefault()}>
                <div className="pg-radio-group">
                  <label className="pg-radio-label">
                    <input 
                      type="radio" 
                      value="sample"
                      checked={generationMode === 'sample'}
                      onChange={() => setGenerationMode('sample')}
                    />
                    <span className="pg-radio-custom"></span>
                    I'll provide a sample post.
                  </label>

                  <label className="pg-radio-label">
                    <input 
                      type="radio" 
                      value="topic"
                      checked={generationMode === 'topic'}
                      onChange={() => setGenerationMode('topic')}
                    />
                    <span className="pg-radio-custom"></span>
                    I'll provide only post topic.
                  </label>
                </div>

                <div className="pg-input-group">
                  <textarea
                    className="pg-textarea"
                    placeholder="Sample Post or Post Topic (Based on your choice)"
                    rows={8}
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                  />
                </div>

                <label className="pg-checkbox-container">
                  <div className="pg-checkbox-input-wrapper">
                    <input 
                      type="checkbox" 
                      checked={requireApproval}
                      onChange={(e) => setRequireApproval(e.target.checked)}
                    />
                    <div className="pg-checkbox-custom">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                    </div>
                  </div>
                  <div className="pg-checkbox-text-group">
                    <span className="pg-checkbox-title">
                      Please share the draft with me for any necessary edits and final approval before posting.
                    </span>
                    <span className="pg-checkbox-subtitle">
                      If this option is left unchecked, you will have 'view-only' access prior to posting, and no edits will be permitted.
                    </span>
                  </div>
                </label>

                <div className="pg-button-row">
                  <button 
                    className="pg-submit-btn pg-btn-primary" 
                    type="button"
                    disabled={inputText.trim() === '' || isGenerating}
                    onClick={handleGeneratePost}
                  >
                    {isGenerating ? "Generating..." : "Generate Post \u2192"}
                  </button>
                </div>
              </form>
            </>
          ) : (
            /* --- STEP 2 & 3: SEE POST (VIEW OR EDIT) --- */
            <>
              <h2 className="pg-title">
                {requireApproval 
                  ? "You chose to have 'Edit & Approve' privileges, here is your post, tune it to your liking!" 
                  : "You chose to have 'View Only' privileges, here is your post!"}
              </h2>
              
              {requireApproval && (
                <p className="pg-subtitle-link">Edit by selecting the text below.</p>
              )}

              <form className="pg-form-wrapper" onSubmit={(e) => e.preventDefault()}>
                <div className="pg-input-group">
                  <textarea
                    className={requireApproval ? "pg-textarea-editable" : "pg-textarea-readonly"}
                    readOnly={!requireApproval}
                    value={generatedText}
                    onChange={(e) => requireApproval && setGeneratedText(e.target.value)}
                    rows={12}
                  />
                </div>

                <div className="pg-action-area">
                  <div className="pg-button-row">
                    <button className="pg-submit-btn pg-btn-primary" type="button" onClick={() => handlePostAction('schedule')} disabled={isScheduling}>
                      {isScheduling ? "Processing..." : (requireApproval ? "Approve & Schedule Post" : "Schedule Post")}
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{marginLeft: '8px'}}>
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                      </svg>
                    </button>
                    
                    <button className="pg-submit-btn pg-btn-primary" type="button" onClick={() => handlePostAction('now')} disabled={isScheduling}>
                      {isScheduling ? "Processing..." : (requireApproval ? "Approve & Post Now \u2192" : "Post Now \u2192")}
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
            </>
          )}
        </section>

        {/* --- STEP 3: SUCCESS MODAL OVERLAY --- */}
        {currentStep === 3 && (
          <>
            <div className="pg-overlay" aria-hidden="true" />
            <section className="pg-success-modal" aria-label="Success confirmation">
              <div className="pg-success-icon" aria-hidden="true">
                &#10003;
              </div>
              <h3>SUCCESS!</h3>
              <p>
                To view or modify the posted post, 
                please navigate to Facebook.
              </p>
              <button 
                className="pg-success-continue" 
                type="button" 
                onClick={() => navigate('/dashboard')}
              >
                Continue
              </button>
            </section>
          </>
        )}
      </main>
    </div>
  );
}
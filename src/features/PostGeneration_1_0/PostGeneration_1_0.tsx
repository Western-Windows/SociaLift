import { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import './PostGeneration_1_0.css';

export interface PostGeneration_1_0Props {
  // Define props here
}

export function PostGeneration_1_0({}: PostGeneration_1_0Props) {
  const navigate = useNavigate(); // Initialize the navigate function

  // State for interactive elements
  const [generationMode, setGenerationMode] = useState('sample');
  const [requireApproval, setRequireApproval] = useState(true);
  
  // State to track the text box content
  const [postText, setPostText] = useState('');

  // Handler for the Generate Post button
  const handleGeneratePost = () => {
    if (requireApproval) {
      navigate('/post-gen1-1a');
    } else {
      navigate('/post-gen1-1b');
    }
  };

  return (
    <div className="post-generation-container">
      <main className="pg-main-layout">
        
        {/* SIDEBAR */}
        <aside className="pg-sidebar">
          <div className="pg-step">
            <span className="pg-step-num pg-active-num">1</span>
            <span className="pg-step-text pg-active-text">Generate Post</span>
          </div>

          {/* Thick vertical line connecting steps */}
          <div className="pg-step-line"></div>

          <div className="pg-step">
            <span className="pg-step-num pg-idle-num">2</span>
            <span className="pg-step-text">See post</span>
          </div>

          <div className="pg-badge">In progress</div>
        </aside>

        {/* MAIN CONTENT CARD */}
        <section className="pg-form-card">
          <h2 className="pg-title">How would you like to generate this new post?</h2>
          <p className="pg-subtitle">
            You may provide a sample post for us to follow, or you can leave the creative direction to us and simply provide the topic.
          </p>

          <form className="pg-form-wrapper" onSubmit={(e) => e.preventDefault()}>
            
            {/* Custom Radio Group */}
            <div className="pg-radio-group">
              <label className="pg-radio-label">
                <input 
                  type="radio" 
                  name="generationMode" 
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
                  name="generationMode" 
                  value="topic"
                  checked={generationMode === 'topic'}
                  onChange={() => setGenerationMode('topic')}
                />
                <span className="pg-radio-custom"></span>
                I'll provide only post topic.
              </label>
            </div>

            {/* Text Area */}
            <div className="pg-input-group">
              <textarea
                className="pg-textarea"
                placeholder="Sample Post or Post Topic (Based on your choice)"
                rows={8}
                value={postText}
                onChange={(e) => setPostText(e.target.value)}
              />
            </div>

            {/* Custom Checkbox Area */}
            <label className="pg-checkbox-container">
              <div className="pg-checkbox-input-wrapper">
                <input 
                  type="checkbox" 
                  checked={requireApproval}
                  onChange={(e) => setRequireApproval(e.target.checked)}
                />
                <div className="pg-checkbox-custom">
                  {/* SVG Checkmark */}
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

            {/* Submit Button */}
            <div className="pg-button-row">
              <button 
                className="pg-submit-btn" 
                type="button"
                disabled={postText.trim() === ''}
                onClick={handleGeneratePost} /* Added onClick handler here */
              >
                Generate Post &rarr;
              </button>
            </div>
          </form>
        </section>
      </main>
    </div>
  );
}
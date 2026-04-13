import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Signup.css';
import { Input, Button } from '../../components/components';
import logo from '../../assets/SociaLift logo 5.svg';
import dashboard1 from '../../assets/dashboard 1.svg';
import actionable1 from '../../assets/actionable 1.svg';
import content1 from '../../assets/content 1.svg';
import interface1 from '../../assets/interface 1.svg';
import messenger1 from '../../assets/messenger 1.svg';
import socialmedia1 from '../../assets/social-media-marketing 1.svg';

export function Signup() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false
  });

  const handleNext = () => {
    if (step === 1) setStep(2);
    else {
      // Handle Final Submit
      console.log('Form Submitted', formData);
      // Navigate to Getting Started Step 1
      navigate('/getting-started');
    }
  };

  const handlePrev = () => {
    if (step === 2) setStep(1);
  };

  const togglePassword = () => setShowPassword(!showPassword);

  // Validation Logic
  const isStep1Valid = 
    formData.username.trim() !== '' && 
    formData.email.trim() !== '' && 
    formData.password.trim() !== '' && 
    formData.confirmPassword.trim() !== '' &&
    formData.password === formData.confirmPassword; // Ensures passwords match

  const isStep2Valid = true; // For now, we can assume step 2 is always valid since it's just informational and a checkbox

  const canProceed = step === 1 ? isStep1Valid : isStep2Valid;

  const PasswordToggle = (
    <div className="password-toggle" onClick={togglePassword} style={{ cursor: 'pointer' }}>
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
        <circle cx="12" cy="12" r="3"></circle>
      </svg>
      <span>{showPassword ? 'Hide' : 'Show'}</span>
    </div>
  );

  return (
    <div className="viewport-container">
      <div className="login-content-wrapper">
        <div className="signup-card">
          {/* Back Button */}
          {step === 2 && (
            <button className="back-arrow" onClick={handlePrev} aria-label="Go back">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#07265C" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
            </button>
          )}

          {/* Header Section */}
          <div className="header-section">
            <div className="logo-wrapper">
              <img src={logo} alt="SociaLift Logo" className="login-logo" />
            </div>
            <h1 className="title">Sign up</h1>
            <p className="subtitle">
              Already have an account on SociaLift? <a href="/login" className="link">Sign in</a>
            </p>
          </div>

          {/* Step Indicator (The Slider in the middle) */}
          <div className="step-indicator-container">
            <div className="step-line">
              <div className={`step-line-active step-${step}`}></div>
            </div>
            <div className="step-points">
              <div className="step-point-wrapper">
                <div className={`step-point ${step >= 1 ? 'active' : ''}`}>1</div>
                <span className={`step-label ${step === 1 ? 'active' : ''}`}>Enter your credentials</span>
              </div>
              <div className="step-point-wrapper">
                <div className={`step-point ${step >= 2 ? 'active' : ''}`}>2</div>
                <span className={`step-label ${step === 2 ? 'active' : ''}`}>Provide Facebook access</span>
              </div>
            </div>
          </div>

          <div className="form-container">
            <div className={`steps-wrapper step-${step}`}>
              {/* Step 1: Credentials */}
              <div className={`step-content ${step === 1 ? 'active' : ''}`}>
                <div className="grid-2-cols">
                  <Input
                    label="Username"
                    placeholder="Enter username"
                    value={formData.username}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, username: e.target.value })}
                  />
                  <Input
                    label="Email address"
                    placeholder="Enter email address"
                    type="email"
                    value={formData.email}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, email: e.target.value })}
                  />
                  <Input
                    label="Password"
                    placeholder="Enter password"
                    type={showPassword ? 'text' : 'password'}
                    rightElement={PasswordToggle}
                    value={formData.password}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, password: e.target.value })}
                  />
                  <Input
                    label="Confirm password"
                    placeholder="Confirm password"
                    type={showPassword ? 'text' : 'password'}
                    rightElement={PasswordToggle}
                    value={formData.confirmPassword}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  />
                </div>
              </div>

              {/* Step 2: Facebook Access */}
              <div className={`step-content ${step === 2 ? 'active' : ''}`}>
                <div className="access-cards">
                  <div className="access-card">
                    <div className="card-icons">
                      <img src={dashboard1} alt="Dashboard Image" className="card-logo" />
                      <img src={actionable1} alt="Actionable Image" className="card-logo" />
                    </div>
                    <h3>PAGE INSIGHTS & ANALYTICS DATA</h3>
                    <p>We will only analyze data from your page and performance. (no personal data collected)</p>
                  </div>
                  <div className="access-card">
                    <div className="card-icons">
                      <img src={content1} alt="Content Image" className="card-logo" />
                      <img src={socialmedia1} alt="Social Media Image" className="card-logo" />
                    </div>
                    <h3>CONTENT PUBLISHING & MODERATION</h3>
                    <p>Permits SociaLift to schedule and publish new posts, and read/post comments on your page.</p>
                  </div>
                  <div className="access-card">
                    <div className="card-icons">
                      <img src={messenger1} alt="Messenger Image" className="card-logo" />
                      <img src={interface1} alt="Interface Image" className="card-logo" />
                    </div>
                    <h3>DIRECT MESSAGING INTEGRATION</h3>
                    <p>Enables us to receive user messages and send replies on your behalf from your page.</p>
                  </div>
                </div>

                <div className="terms-checkbox">
                  <input
                    type="checkbox"
                    id="terms"
                    checked={formData.agreeToTerms}
                    onChange={(e) => setFormData({ ...formData, agreeToTerms: e.target.checked })}
                  />
                  <label htmlFor="terms">By creating an account, I agree to our <a href="#">Terms of use</a> and <a href="#">Privacy Policy</a></label>
                </div>

                <button className="fb-signup-btn">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="#1877F2"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                  Sign up with Facebook
                </button>
              </div>
            </div>
          </div>

          {/* Primary Action Button */}
          <div className="action-button-wrapper">
             <Button 
               onClick={handleNext} 
               disabled={!canProceed}
               style={{ opacity: canProceed ? 1 : 0.5, cursor: canProceed ? 'pointer' : 'not-allowed' }}
             >
                {step === 1 ? 'Next' : 'Create Account'}
             </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
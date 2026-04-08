import React, { useState } from 'react'; 
import { Eye, EyeSlash } from '@phosphor-icons/react/dist/ssr'; 
import './Login.css'; 
import { Input, Button, Divider } from '../../components/components';
import loginBg from '../../assets/Login Background.png';
import logo from '../../assets/SociaLift logo 5.svg';

export function Login() {
  const [showPassword, setShowPassword] = useState<boolean>(false);

  // TODO: Implement actual sign-in logic
  const handleSignIn = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log("Sign in clicked");
  };

  // TODO: Implement Facebook OAuth logic
  const handleFacebookLogin = () => {
    console.log("Facebook login clicked");
  };

  return (
    <div className="viewport-container">
      <div className="login-window">
        {/* Background Image */}
        <img src={loginBg} alt="Background" className="login-bg" />

        <div className="login-content-wrapper">
          <div className="login-card">
            
            {/* Header Section */}
            <div className="header-section">
              <div className="logo-wrapper">
                <img src={logo} alt="SociaLift Logo" className="login-logo" />
              </div>
              <h1 className="title">
                Sign in
              </h1>
              <p className="subtitle">
                New to SocialLift?{' '}
                <a href="/signup" className="link">
                  Sign up for free
                </a>
              </p>
            </div>

            {/* Form Section */}
            <form onSubmit={handleSignIn}>
              <Input 
                label="Email address" 
                id="email" 
                type="email" 
                placeholder="Enter your email"
              />
              
              <Input 
                label="Password" 
                id="password" 
                type={showPassword ? "text" : "password"} 
                rightElement={
                  <div className="password-toggle" onClick={() => setShowPassword(!showPassword)}>
                    {showPassword ? <Eye size={16} /> : <EyeSlash size={16} />}
                    <span>
                      {showPassword ? "Hide" : "Show"}
                    </span>
                  </div>
                }
              />

              <div className="forgot-password-wrapper">
                <a href="/forgot-password" className="link" style={{ fontSize: '0.775rem' }}>
                  Forget password?
                </a>
              </div>

              <Button type="submit" variant="primary">
                Sign in
              </Button>
            </form>

            <Divider text="OR" />

            {/* Social Login Section */}
            <Button 
              type="button" 
              variant="outline" 
              onClick={handleFacebookLogin}
              icon={
                <svg
                  className="facebook-icon"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  width="20"
                  height="20"
                >
                  <path
                    d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.469h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.469h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"
                    fill="#1877F2"
                  />
                  <path
                    d="M16.671 15.542l.532-3.469h-3.328v-2.25c0-.949.465-1.874 1.956-1.874h1.514V5.011s-1.374-.235-2.686-.235c-2.741 0-4.533 1.662-4.533 4.669v2.628H7.078v3.469h3.047v8.385a12.09 12.09 0 003.75 0v-8.385h2.796z"
                    fill="#fff"
                  />
                </svg>
              }
            >
              Continue with Facebook
            </Button>

          </div>
        </div>
      </div>
    </div>
  );
}

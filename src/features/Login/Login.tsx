import React, { useState, useEffect } from 'react'; 
import { useNavigate } from 'react-router-dom';
import { Eye, EyeSlash } from '@phosphor-icons/react/dist/ssr'; 
import './Login.css'; 
import { Input, Button, Divider } from '../../components/components';
import loginBg from '../../assets/Login Background.png';
import logo from '../../assets/SociaLift logo 5.svg';

export function Login() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // 1. Load the official Facebook SDK natively
  useEffect(() => {
    (window as any).fbAsyncInit = function() {
      (window as any).FB.init({
        appId      : '1104505465230235',
        cookie     : true,
        xfbml      : true,
        version    : 'v19.0'
      });
    };

    (function(d, s, id) {
      var js: any, fjs = d.getElementsByTagName(s)[0];
      if (d.getElementById(id)) return;
      js = d.createElement(s); js.id = id;
      js.src = "https://connect.facebook.net/en_US/sdk.js";
      fjs?.parentNode?.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));
  }, []);

  const handleSignIn = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Login failed");
      }
      
      const data = await response.json();
      localStorage.setItem("socialift_user_id", data.user_id.toString());
      localStorage.setItem("socialift_username", data.username);
      
      navigate('/home');
    } catch (error: any) {
      console.error("Error signing in:", error.message);
    }
  };

  const handleFacebookSuccess = async (accessToken: string) => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/auth/facebook`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ accessToken, is_signup: false })
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Backend verification failed");
      }

      const data = await res.json();
      localStorage.setItem("socialift_user_id", data.user_id.toString());
      localStorage.setItem("socialift_username", data.username || "User");
      navigate('/home');
    } catch (error: any) {
      console.error("Error during Facebook login sync:", error);
      alert(error.message);
    }
  };

  // 2. Trigger the native login popup
  const handleFacebookLogin = () => {
    (window as any).FB.login(
      (response: any) => {
        if (response.authResponse && response.authResponse.accessToken) {
          handleFacebookSuccess(response.authResponse.accessToken);
        } else {
          console.log('User cancelled login or did not fully authorize.');
        }
      },
      { scope: "pages_show_list,pages_read_engagement,pages_manage_posts" }
    );
  };

  const isFormValid = email.trim() !== '' && password.trim() !== '';

  return (
    <div className="viewport-container">
      <div className="login-window">
        <img src={loginBg} alt="Background" className="login-bg" />
        <div className="login-content-wrapper">
          <div className="login-card">
            
            <div className="header-section">
              <div className="logo-wrapper">
                <img src={logo} alt="SociaLift Logo" className="login-logo" />
              </div>
              <h1 className="title">Sign in</h1>
              <p className="subtitle">
                New to SocialLift? <a href="/signup" className="link">Sign up for free</a>
              </p>
            </div>

            <form onSubmit={handleSignIn}>
              <Input 
                label="Email address" 
                id="email" 
                type="email" 
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <Input 
                label="Password" 
                id="password" 
                type={showPassword ? "text" : "password"} 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                rightElement={
                  <div className="password-toggle" onClick={() => setShowPassword(!showPassword)} style={{ cursor: 'pointer' }}>
                    {showPassword ? <Eye size={16} /> : <EyeSlash size={16} />}
                    <span>{showPassword ? "Hide" : "Show"}</span>
                  </div>
                }
              />
              <div className="forgot-password-wrapper">
                <a href="/forgot-password" className="link" style={{ fontSize: '0.775rem' }}>Forget password?</a>
              </div>
              <Button type="submit" variant="primary" disabled={!isFormValid} style={{ opacity: isFormValid ? 1 : 0.5, cursor: isFormValid ? 'pointer' : 'not-allowed' }}>
                Sign in
              </Button>
            </form>

            <Divider text="OR" />

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
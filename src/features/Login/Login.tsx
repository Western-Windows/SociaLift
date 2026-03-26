import './Login.css';

// 1. Automatically scaffold the TypeScript interface
export interface LoginProps {
// Define props here
}

// 2. Clean, compiler-friendly functional component
export function Login({}: LoginProps) {
return (
<div className="login">
    <h1>Login</h1>
</div>
);
}
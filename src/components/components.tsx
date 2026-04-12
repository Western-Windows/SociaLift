import React from 'react';

// Possible Custom Component: Input
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  rightElement?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({ label, id, rightElement, ...props }) => {
  return (
    <div className="input-group">
      <label htmlFor={id} className="input-label">{label}</label>
      <div className="input-wrapper">
        <input id={id} className="input-field" {...props} />
        {rightElement && <div className="input-right-element">{rightElement}</div>}
      </div>
    </div>
  );
};

// Possible Custom Component: Button
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'outline';
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({ children, variant = 'primary', icon, ...props }) => {
  return (
    <button className={`btn btn-${variant}`} {...props}>
      {icon && <span className="btn-icon">{icon}</span>}
      {children}
    </button>
  );
};

// Possible Custom Component: Divider
interface DividerProps {
  text?: string;
}

export const Divider: React.FC<DividerProps> = ({ text }) => {
  return (
    <div className="divider">
      <hr />
      {text && <span className="divider-text">{text}</span>}
      <hr />
    </div>
  );
};

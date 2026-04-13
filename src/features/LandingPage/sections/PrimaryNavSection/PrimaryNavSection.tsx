import { useNavigate } from 'react-router-dom';

interface PrimaryNavSectionProps {
  onSignIn?: () => void;
  onSignUp?: () => void;
}

export const PrimaryNavSection = ({ onSignIn, onSignUp }: PrimaryNavSectionProps): JSX.Element => {
  const navigate = useNavigate(); // <-- Initialize hook

  return (
    <div className="absolute top-[18px] left-[-23px] w-[1536px] h-[81px]">
      <div className="absolute top-0 left-0 w-[1536px] h-[72px] flex items-center justify-end">
        <div className="inline-flex h-[52px] mr-6 w-[308px] relative items-center justify-center gap-4">

          {/* Sign In Button */}
          <button
            type="button"
            onClick={() => {
              if (onSignIn) onSignIn();
              navigate('/login'); // <-- Route to login
            }}
            className="all-[unset] box-border relative flex items-center justify-center w-[146px] h-[52px] rounded-lg overflow-hidden border border-solid border-[#07265c] cursor-pointer"
          >
            <div className="inline-flex items-center justify-center gap-2">
              <div className="relative flex items-center justify-center w-fit [font-family:'Poppins',Helvetica] font-normal text-[#07265c] text-[25px] text-center tracking-[0] leading-[normal]">
                Sign in
              </div>
            </div>
          </button>

          {/* Sign Up Button */}
          <button
            type="button"
            onClick={() => {
              if (onSignUp) onSignUp();
              navigate('/signup'); // <-- Route to signup
            }}
            className="all-[unset] box-border relative flex items-center justify-center w-[146px] h-[52px] bg-[#07265c] rounded-lg overflow-hidden border border-solid cursor-pointer mr-[20px]"
          >
            <div className="inline-flex items-center justify-center gap-2">
              <div className="relative flex items-center justify-center w-fit [font-family:'Poppins',Helvetica] font-normal text-white text-[25px] text-center tracking-[0] leading-[normal]">
                Sign up
              </div>
            </div>
          </button>
        </div>
      </div>

      <img
        className="absolute top-0 left-[150px] w-[76px] h-[81px] aspect-[0.93]"
        alt="Socialift logo"
        src="https://c.animaapp.com/hFv7aPLp/img/socialift-logo-5@2x.png"
      />
    </div>
  );
};
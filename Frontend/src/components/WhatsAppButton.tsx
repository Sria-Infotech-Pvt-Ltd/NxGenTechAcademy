import { FaWhatsapp } from "react-icons/fa";
import { Phone } from "lucide-react";
import { useState } from "react";

// Global floating contact buttons.
// Rendered once in App.tsx so it appears on every page - before login,
// after login, and on every dashboard - instead of being duplicated
// per-page.
const WHATSAPP_NUMBER = "919059585039";
const PHONE_NUMBER = "+91-90595 85039";
const PHONE_RAW = "919059585039";
const WHATSAPP_MESSAGE = "Hi, I'm interested in courses at NxGen Tech Academy";

export const WhatsAppButton = () => {
  const [showPhoneTooltip, setShowPhoneTooltip] = useState(false);

  return (
    <div className="fixed right-6 bottom-6 z-50 flex flex-col gap-4 items-end">
      {/* Phone Icon Button - reveals number on hover (desktop) or click (mobile) */}
      <div
        className="relative"
        onMouseEnter={() => setShowPhoneTooltip(true)}
        onMouseLeave={() => setShowPhoneTooltip(false)}
      >
        <button
          type="button"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setShowPhoneTooltip(!showPhoneTooltip);
          }}
          aria-label="Show phone number"
          className="flex items-center justify-center w-14 h-14 rounded-full bg-[#000080] text-white shadow-lg hover:shadow-xl hover:scale-110 transition-transform"
        >
          <Phone className="w-6 h-6" />
        </button>

        {/* Tooltip with phone number - appears on hover/click */}
        {showPhoneTooltip && (
          <div className="absolute right-16 top-1/2 -translate-y-1/2 bg-white rounded-lg shadow-lg border border-gray-200 px-4 py-3 whitespace-nowrap animate-in fade-in slide-in-from-right-2 duration-200 z-10">
            <a
              href={`tel:+${PHONE_RAW}`}
              onClick={(e) => e.stopPropagation()}
              className="text-[#000080] font-semibold hover:underline no-underline"
            >
              {PHONE_NUMBER}
            </a>
          </div>
        )}
      </div>

      {/* WhatsApp Button - separate from phone */}
      <a
        type="button"
        aria-label="Chat on WhatsApp"
        href={`https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(WHATSAPP_MESSAGE)}`}
        target="_blank"
        rel="noreferrer noopener"
        className="flex items-center justify-center w-14 h-14 relative"
        onClick={(e) => e.stopPropagation()}
      >
        <span className="absolute inset-0 rounded-full bg-green-500 opacity-75 animate-ping"></span>
        <span className="relative flex items-center justify-center w-14 h-14 rounded-full bg-green-600 text-white shadow-lg animate-bounce transition-transform hover:scale-110">
          <FaWhatsapp className="w-8 h-8" />
        </span>
      </a>
    </div>
  );
};

export default WhatsAppButton;

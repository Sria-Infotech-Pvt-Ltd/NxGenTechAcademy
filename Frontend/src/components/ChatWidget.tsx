import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  X,
  ArrowRight,
  RefreshCw,
  AlertCircle,
  Maximize2,
  Minimize2
} from "lucide-react";
import chatbotLogo from "@/assets/chatbot-logo.png";
import { chatbotService, ChatbotResponse } from "@/services/chatbotService";

interface Message {
  id: string;
  sender: "user" | "bot";
  text: string;
  timestamp: string;
  found?: boolean;
  course_name?: string | null;
  course_slug?: string | null;
  section?: string | null;
  similarity?: number;
  action_type?: string | null;
  action_url?: string | null;
  action_text?: string | null;
  isError?: boolean;
}

const INITIAL_GREETING: Message = {
  id: "initial-greeting",
  sender: "bot",
  text: "Hi! 👋 How can I help you today?",
  timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
};

const INITIAL_RECOMMENDATIONS = [
  "🚀 Explore our courses",
  "🎯 Find a course for my career",
  "💼 Explore placement opportunities",
  "💰 Check fees & duration",
];

interface TypewriterMessageProps {
  text: string;
  isInitial?: boolean;
  onScroll?: () => void;
  renderMarkdown: (text: string) => React.ReactNode;
}

const TypewriterMessage: React.FC<TypewriterMessageProps> = ({
  text,
  isInitial = false,
  onScroll,
  renderMarkdown,
}) => {
  const [displayedText, setDisplayedText] = useState<string>(isInitial ? text : "");
  const [isTyping, setIsTyping] = useState<boolean>(!isInitial && Boolean(text));

  useEffect(() => {
    if (isInitial || !text) {
      setDisplayedText(text);
      setIsTyping(false);
      return;
    }

    let currentIndex = 0;
    setDisplayedText("");
    setIsTyping(true);

    const intervalId = setInterval(() => {
      currentIndex += 1;
      setDisplayedText(text.slice(0, currentIndex));
      if (onScroll) {
        onScroll();
      }

      if (currentIndex >= text.length) {
        clearInterval(intervalId);
        setIsTyping(false);
        if (onScroll) {
          onScroll();
        }
      }
    }, 10);

    return () => {
      clearInterval(intervalId);
    };
  }, [text, isInitial]);

  return (
    <div>
      <div>{renderMarkdown(displayedText)}</div>
      {isTyping && (
        <span
          className="inline-block w-1.5 h-3.5 ml-1 bg-[#000080] align-middle animate-pulse rounded-xs"
          aria-hidden="true"
        />
      )}
    </div>
  );
};

export const ChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [messages, setMessages] = useState<Message[]>([INITIAL_GREETING]);
  const [inputQuery, setInputQuery] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeCourse, setActiveCourse] = useState<{ name: string; slug: string } | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen, messages, isLoading]);

  const handleSendMessage = async (queryToSend?: string) => {
    const query = (queryToSend || inputQuery).trim();
    if (!query || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputQuery("");
    setIsLoading(true);

    try {
      const response: ChatbotResponse = await chatbotService.searchKnowledgeBase(query, activeCourse);

      // Only set activeCourse when BOTH course_name and course_slug exist and represent an actual course
      if (
        response.found &&
        response.action_type !== "book_demo" &&
        response.course_name &&
        response.course_slug &&
        response.course_slug.trim() !== ""
      ) {
        setActiveCourse({
          name: response.course_name,
          slug: response.course_slug.trim(),
        });
      }

      const botMessage: Message = {
        id: `bot-${Date.now()}`,
        sender: "bot",
        text: response.reply || "I couldn't find specific information about that.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        found: response.found,
        course_name: response.course_name || response.course,
        course_slug: response.course_slug,
        section: response.section,
        similarity: response.similarity,
        action_type: response.action_type,
        action_url: response.action_url,
        action_text: response.action_text,
        isError: false,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err: any) {
      let errorText = "Sorry, I'm having trouble connecting right now. Please try again.";
      if (err?.response?.status === 429) {
        errorText = "Too many requests. Please wait a moment before sending another message.";
      } else if (err?.response?.data?.error) {
        errorText = String(err.response.data.error);
      }

      const errorMessage: Message = {
        id: `err-${Date.now()}`,
        sender: "bot",
        text: errorText,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        found: false,
        isError: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleNavigation = (pathOrSlug: string) => {
    if (!pathOrSlug) return;
    if (pathOrSlug.startsWith("/")) {
      navigate(pathOrSlug);
    } else if (pathOrSlug === "sap-courses") {
      navigate("/courses/sap-courses");
    } else {
      navigate(`/courses/${pathOrSlug}`);
    }
  };

  const handleCourseNavigation = handleNavigation;

  const getBroadCatalogUrl = (msg: Message): string | null => {
    if (!msg.found) return null;
    if (msg.action_type === "book_demo" || msg.action_text === "Book Demo") return null;
    if (msg.course_slug && msg.course_slug.trim() !== "") return null;
    const text = msg.text.toLowerCase();
    if (text.includes("digital marketing") || text.includes("job guarantee digital marketing")) {
      return "/training-programs?category=Digital+Marketing";
    }
    if (
      text.includes("sap technical") ||
      text.includes("sap functional") ||
      text.includes("what sap courses") ||
      text.includes("courses faqs") ||
      (text.includes("sap") && text.includes("we offer")) ||
      (text.includes("sap") && text.includes("btp"))
    ) {
      return "/training-programs?category=SAP+Courses";
    }
    return null;
  };

  const handleResetChat = () => {
    setActiveCourse(null);
    setMessages([
      {
        ...INITIAL_GREETING,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
  };

  // Safe structured markdown parser converting raw response text into React nodes
  const renderMarkdownResponse = (text: string): React.ReactNode => {
    if (!text) return null;

    // Helper to parse inline markdown (bold **...**, code `...`, unescaped markdown, HTML entity cleanup)
    const parseInline = (inlineText: string): React.ReactNode => {
      if (!inlineText) return null;
      // Clean up HTML tags, entities, escaped asterisks, stray table boundary pipes, and heading prefixes
      const cleaned = inlineText
        .replace(/<br\s*\/?>/gi, " ")
        .replace(/<\/br>/gi, " ")
        .replace(/<\/?[a-zA-Z][^>]*>/g, "")
        .replace(/&nbsp;/gi, " ")
        .replace(/&amp;/gi, "&")
        .replace(/&lt;/gi, "<")
        .replace(/&gt;/gi, ">")
        .replace(/&quot;/gi, '"')
        .replace(/&#39;/gi, "'")
        .replace(/\\\*/g, "*")
        .replace(/^####\s*/, "")
        .replace(/^###\s*/, "")
        .replace(/^##\s*/, "")
        .replace(/^#\s*/, "")
        .replace(/^\|\s*/, "")
        .replace(/\s*\|$/, "")
        .trim();

      const parts = cleaned.split(/(\*\*.*?\*\*|`.*?`)/g);

      return parts.map((part, partIdx) => {
        if (part.startsWith("**") && part.endsWith("**") && part.length >= 4) {
          return (
            <strong key={partIdx} className="font-semibold text-slate-900">
              {part.slice(2, -2)}
            </strong>
          );
        }
        if (part.startsWith("`") && part.endsWith("`") && part.length >= 2) {
          return (
            <code
              key={partIdx}
              className="bg-slate-100 text-[#000080] px-1 py-0.5 rounded font-mono text-[11px]"
            >
              {part.slice(1, -1)}
            </code>
          );
        }
        return <span key={partIdx}>{part}</span>;
      });
    };

    const lines = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
    type Block =
      | { type: "course_header"; text: string }
      | { type: "section_header"; text: string }
      | { type: "h1" | "h2" | "h3"; text: string }
      | { type: "bullet"; items: string[] }
      | { type: "number"; items: Array<[string, string]> }
      | { type: "p"; text: string }
      | { type: "source_link"; url?: string }
      | { type: "empty" };

    const blocks: Block[] = [];
    let currentList: Block | null = null;

    const flushList = () => {
      if (currentList) {
        blocks.push(currentList);
        currentList = null;
      }
    };

    const headerKeywords = new Set([
      "#", "s.no", "sr.no", "sr no", "sno", "no", "module", "modules", "module name", "module no",
      "topic", "topics", "key topics", "key topics covered", "aspect", "details",
      "description", "course", "course name", "duration", "mode", "fees", "fee",
      "parameter", "value", "feature", "features", "benefit", "benefits", "item",
      "title", "content", "curriculum"
    ]);

    for (const rawLine of lines) {
      const trimmed = rawLine.trim();

      // Skip markdown divider lines (e.g. ---, ___, ***)
      if (trimmed === "---" || trimmed === "___" || trimmed === "***") {
        continue;
      }

      // Check for Markdown table divider row: |---|---| or |--------|------------|
      if (/^\s*\|?[\s\-:|]+\|?\s*$/.test(trimmed) && trimmed.includes("-")) {
        continue;
      }

      // Skip generic internal section content headers
      if (trimmed === "Section: Content") {
        continue;
      }

      // Check for Markdown table rows (e.g. | Module | Topics | or | Module 1 | Topics... |)
      if (trimmed.startsWith("|") && (trimmed.endsWith("|") || trimmed.includes("|"))) {
        const rawCells = trimmed
          .replace(/^\s*\|/, "")
          .replace(/\|\s*$/, "")
          .split("|")
          .map((c) => c.trim());

        const cells = rawCells.filter((c) => c.length > 0);

        // Check if this is a table header row (e.g. | Module | Key Topics |)
        const isHeaderRow =
          cells.length > 0 &&
          cells.every((c) => {
            const normalized = c.toLowerCase().replace(/[*_:`#]/g, "").trim();
            return headerKeywords.has(normalized);
          });

        if (isHeaderRow) {
          continue; // Skip table header
        }

        if (cells.length === 1) {
          flushList();
          const cleanText = cells[0].replace(/<br\s*\/?>|<\/br>/gi, " ").replace(/\*\*/g, "").trim();
          if (/^(module|phase|section|project|\d+\.)/i.test(cleanText)) {
            blocks.push({ type: "h3", text: cleanText });
          } else {
            blocks.push({ type: "p", text: cells[0] });
          }
          continue;
        }

        if (cells.length === 2) {
          flushList();
          const col1 = cells[0].replace(/<br\s*\/?>|<\/br>/gi, " ").trim();
          const col2 = cells[1];

          const cleanCol1 = col1.replace(/\*\*/g, "").trim();

          // Extract bullet topics from col2
          const normCol2 = col2.replace(/<br\s*\/?>/gi, "\n").replace(/<\/br>/gi, "\n");
          let subItems: string[] = [];

          if (normCol2.includes("\n")) {
            subItems = normCol2.split("\n").map((s) => s.trim()).filter(Boolean);
          } else if (normCol2.includes("•")) {
            subItems = normCol2.split("•").map((s) => s.trim()).filter(Boolean);
          } else if (normCol2.includes(";")) {
            subItems = normCol2.split(";").map((s) => s.trim()).filter(Boolean);
          } else if (
            /,/.test(normCol2) &&
            (/^(module|phase|section|project|\d+\.)/i.test(cleanCol1) || cleanCol1.toLowerCase().includes("module"))
          ) {
            subItems = normCol2.split(",").map((s) => s.trim()).filter(Boolean);
          } else {
            subItems = [normCol2.trim()];
          }

          const cleanedSubItems = subItems
            .map((it) => it.replace(/^[-*•\u2022\d\.)\s]+/, "").trim())
            .filter(Boolean);

          const isHeaderLike =
            /^(module|phase|section|project|\d+\.)/i.test(cleanCol1) ||
            cleanCol1.toLowerCase().includes("module") ||
            (cleanedSubItems.length > 1 && !/^(duration|fees?|eligibility|mode|certification|batch|timings?|audience|pre-?requisites?)/i.test(cleanCol1));

          const isAttrLike =
            /^(duration|fees?|eligibility|mode|certification|batch|timings?|audience|pre-?requisites?)/i.test(cleanCol1);

          if (isHeaderLike && !isAttrLike) {
            blocks.push({ type: "h3", text: cleanCol1 });
            if (cleanedSubItems.length > 0) {
              blocks.push({ type: "bullet", items: cleanedSubItems });
            }
          } else {
            const desc = cleanedSubItems.join(", ") || normCol2.replace(/<[^>]+>/g, "").trim();
            blocks.push({
              type: "bullet",
              items: [`**${cleanCol1.replace(/:$/, "")}:** ${desc}`],
            });
          }
          continue;
        }

        if (cells.length >= 3) {
          flushList();
          if (/^\d+$/.test(cells[0])) {
            const num = cells[0];
            const title = cells[1].replace(/<[^>]+>/g, "").replace(/\*\*/g, "").trim();
            const details = cells.slice(2).map((c) => c.replace(/<[^>]+>/g, "").trim()).join(" — ");
            blocks.push({
              type: "number",
              items: [[num, `**${title}**${details ? ` — ${details}` : ""}`]],
            });
          } else {
            const title = cells[0].replace(/<[^>]+>/g, "").replace(/\*\*/g, "").trim();
            const details = cells.slice(1).map((c) => c.replace(/<[^>]+>/g, "").trim()).join(" — ");
            blocks.push({
              type: "bullet",
              items: [`**${title}**${details ? ` — ${details}` : ""}`],
            });
          }
          continue;
        }
      }

      // Handle lines that may contain inline <br>, <br/>, </br>, or <p> tags
      const subLines = trimmed.split(/<br\s*\/?>|<\/br>|<\/?p>/gi);

      for (const rawSubLine of subLines) {
        const subTrimmed = rawSubLine.trim();

        // Handle Source reference line: "*Source:* [https://...]" or "Source: ..."
        if (/^(\*?Source:?\*?)/i.test(subTrimmed)) {
          flushList();
          blocks.push({
            type: "source_link",
            url: "/courses/sap-courses",
          });
          continue;
        }

        // Check for bullet list item: '- ...' or '* ...' or '• ...'
        const bulletMatch = subTrimmed.match(/^[-*•]\s+(.*)$/);
        if (bulletMatch) {
          const itemText = bulletMatch[1];
          if (currentList && currentList.type === "bullet") {
            currentList.items.push(itemText);
          } else {
            flushList();
            currentList = { type: "bullet", items: [itemText] };
          }
          continue;
        }

        // Check for numbered list item: '1. ...'
        const numMatch = subTrimmed.match(/^(\d+)\.\s+(.*)$/);
        if (numMatch) {
          const num = numMatch[1];
          const itemText = numMatch[2];
          if (currentList && currentList.type === "number") {
            currentList.items.push([num, itemText]);
          } else {
            flushList();
            currentList = { type: "number", items: [[num, itemText]] };
          }
          continue;
        }

        // Flush open list before handling other non-list lines
        flushList();

        // Empty line
        if (!subTrimmed) {
          blocks.push({ type: "empty" });
          continue;
        }

        // Course header: "Course: Courses FAQs" -> Normalize to "SAP Courses"
        if (subTrimmed.startsWith("Course:")) {
          const courseTitle = subTrimmed.replace(/^Course:\s*/, "").trim();
          const displayTitle = courseTitle === "Courses FAQs" ? "SAP Courses" : courseTitle;
          blocks.push({
            type: "course_header",
            text: displayTitle,
          });
          continue;
        }

        // Section header (e.g. "Section: Certification")
        if (subTrimmed.startsWith("Section:")) {
          blocks.push({
            type: "section_header",
            text: subTrimmed.replace(/^Section:\s*/, "").trim(),
          });
          continue;
        }

        // FAQ Question: "### Q: What SAP courses do you offer?" or "### Q: ..."
        if (subTrimmed.startsWith("### Q:") || subTrimmed.startsWith("### Question:")) {
          const qText = subTrimmed.replace(/^###\s*Q(?:uestion)?:\s*/, "").trim();
          blocks.push({ type: "h3", text: qText });
          continue;
        }

        // Heading 3: '### ...'
        if (subTrimmed.startsWith("### ")) {
          blocks.push({ type: "h3", text: subTrimmed.slice(4).trim() });
          continue;
        }

        // Heading 2: '## ...'
        if (subTrimmed.startsWith("## ")) {
          blocks.push({ type: "h2", text: subTrimmed.slice(3).trim() });
          continue;
        }

        // Heading 1: '# ...'
        if (subTrimmed.startsWith("# ")) {
          blocks.push({ type: "h1", text: subTrimmed.slice(2).trim() });
          continue;
        }

        // FAQ Answer: "**A:** We offer SAP Technical (ABAP on HANA...)"
        if (subTrimmed.startsWith("**A:**") || subTrimmed.startsWith("A:")) {
          const aText = subTrimmed.replace(/^\*\*A:\*\*\s*/, "").replace(/^A:\s*/, "").trim();

          // If the answer contains standard SAP course categorisation, render structured bullets
          if (aText.includes("SAP Technical") && aText.includes("SAP Functional") && aText.includes("SAP BTP")) {
            blocks.push({ type: "p", text: "We offer:" });
            blocks.push({
              type: "bullet",
              items: [
                "SAP Technical — ABAP on HANA, CDS/RAP, Fiori UI5, BASIS",
                "SAP Functional — FICO, MM, SD, PP, QM",
                "SAP BTP — BTP for Professionals, BTP for Freshers, SAP CPI",
              ],
            });
            continue;
          }

          blocks.push({ type: "p", text: aText });
          continue;
        }

        // Normal paragraph
        blocks.push({ type: "p", text: subTrimmed });
      }
    }

    flushList();

    return (
      <div className="space-y-1 leading-relaxed">
        {blocks.map((block, idx) => {
          switch (block.type) {
            case "course_header":
              return (
                <div
                  key={idx}
                  className="font-bold text-sm text-[#000080] border-b border-blue-100 pb-1 mb-2"
                >
                  {parseInline(block.text)}
                </div>
              );

            case "section_header":
              return (
                <div
                  key={idx}
                  className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1"
                >
                  {parseInline(block.text)}
                </div>
              );

            case "h1":
            case "h2":
            case "h3":
              return (
                <h4
                  key={idx}
                  className="font-bold text-xs uppercase tracking-wider text-[#000080] mt-3 mb-1 flex items-center gap-1.5 border-b border-slate-200/60 pb-0.5 first:mt-0"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-[#000080] flex-shrink-0" />
                  <span>{parseInline(block.text)}</span>
                </h4>
              );

            case "bullet":
              return (
                <ul key={idx} className="space-y-1 my-1.5 pl-1">
                  {block.items.map((item, itemIdx) => (
                    <li
                      key={itemIdx}
                      className="flex items-start gap-2 text-slate-700 leading-snug text-[13px]"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-[#000080]/60 mt-1.5 flex-shrink-0" />
                      <span className="flex-1">{parseInline(item)}</span>
                    </li>
                  ))}
                </ul>
              );

            case "number":
              return (
                <ol key={idx} className="space-y-1.5 my-1.5 pl-0.5">
                  {block.items.map(([num, item], itemIdx) => (
                    <li
                      key={itemIdx}
                      className="flex items-start gap-2 text-slate-700 leading-snug text-[13px]"
                    >
                      <span className="font-semibold text-[#000080] text-xs min-w-[16px] flex-shrink-0">
                        {num}.
                      </span>
                      <span className="flex-1">{parseInline(item)}</span>
                    </li>
                  ))}
                </ol>
              );

            case "p":
              return (
                <p key={idx} className="leading-relaxed text-slate-700 my-0.5 text-[13px]">
                  {parseInline(block.text)}
                </p>
              );

            case "source_link":
              return (
                <div
                  key={idx}
                  className="text-[11px] text-slate-500 mt-2.5 pt-1.5 border-t border-slate-100 flex items-center gap-1 select-none"
                >
                  <span>Source: NxGen Tech Academy –</span>
                  <button
                    type="button"
                    onClick={() => handleCourseNavigation(block.url || "sap-courses")}
                    className="text-[#000080] font-semibold hover:underline cursor-pointer inline"
                  >
                    Courses
                  </button>
                </div>
              );

            case "empty":
              return <div key={idx} className="h-1.5" />;

            default:
              return null;
          }
        })}
      </div>
    );
  };

  return (
    <aside
      aria-label="NxGen Tech Academy Chat Assistant Widget"
      className="fixed right-6 bottom-[88px] max-sm:right-4 max-sm:bottom-[80px] z-50 flex flex-col items-end pointer-events-none"
    >
      {/* ───────────────────────────────────────────────────────────── */}
      {/* CHAT WINDOW */}
      {/* ───────────────────────────────────────────────────────────── */}
      <AnimatePresence>
        {isOpen && (
          <motion.section
            aria-label="Chat window"
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.22, ease: "easeOut" }}
            className={`pointer-events-auto ${
              isExpanded
                ? "w-[640px] h-[680px] max-h-[calc(100vh-100px)]"
                : "w-[380px] h-[540px] max-h-[calc(100vh-120px)]"
            } max-w-[calc(100vw-32px)] bg-white rounded-2xl shadow-2xl border border-slate-200/80 flex flex-col overflow-hidden text-slate-800 transition-all duration-300 ease-in-out`}
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-[#000080] via-[#1e3a8a] to-[#2563eb] text-white px-4 py-3 flex items-center justify-between shadow-sm select-none">
              <div className="flex items-center gap-2.5">
                <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-white p-0.5 border border-white/30 shadow-sm flex-shrink-0">
                  <img src={chatbotLogo} alt="NxGen Assistant" className="w-full h-full object-contain rounded-md" />
                  <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-400 border-2 border-[#1e3a8a]" />
                </div>
                <div>
                  <div className="flex items-center gap-1.5">
                    <h3 className="font-semibold text-sm leading-tight text-white">
                      NxGen Assistant
                    </h3>
                  </div>
                  <p className="text-[11px] text-blue-100/80 leading-tight mt-0.5">
                    NxGen Tech Academy Knowledge Base
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={handleResetChat}
                  title="Reset conversation"
                  aria-label="Reset conversation"
                  className="p-1.5 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={() => setIsExpanded((prev) => !prev)}
                  title={isExpanded ? "Restore size" : "Expand chat"}
                  aria-label={isExpanded ? "Restore chat window size" : "Expand chat window"}
                  className="p-1.5 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors flex items-center justify-center"
                >
                  {isExpanded ? (
                    <Minimize2 className="w-4 h-4" />
                  ) : (
                    <Maximize2 className="w-4 h-4" />
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  title="Close chat"
                  aria-label="Close chat"
                  className="p-1.5 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Message Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-slate-50/50 text-sm">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex flex-col ${
                    msg.sender === "user" ? "items-end" : "items-start"
                  }`}
                >
                  <div className="flex items-start gap-2 max-w-[88%]">
                    {msg.sender === "bot" && (
                      <div className="flex-shrink-0 w-6 h-6 rounded-md bg-white border border-slate-200/80 shadow-xs flex items-center justify-center p-0.5 mt-0.5">
                        <img src={chatbotLogo} alt="NxGen Assistant" className="w-full h-full object-contain rounded-xs" />
                      </div>
                    )}

                    <div
                      className={`px-3.5 py-2.5 rounded-2xl shadow-sm ${
                        msg.sender === "user"
                          ? "bg-[#000080] text-white rounded-br-xs font-normal"
                          : msg.isError
                          ? "bg-red-50 text-red-700 border border-red-200 rounded-bl-xs"
                          : "bg-white text-slate-700 border border-slate-200/80 rounded-bl-xs"
                      }`}
                    >
                      {msg.isError ? (
                        <div className="flex items-start gap-2">
                          <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                          <div>{msg.text}</div>
                        </div>
                      ) : msg.sender === "user" ? (
                        <p className="text-white text-[13px] leading-relaxed break-words font-medium">
                          {msg.text}
                        </p>
                      ) : (
                        <div>
                          <TypewriterMessage
                            text={msg.text}
                            isInitial={msg.id === "initial-greeting"}
                            onScroll={scrollToBottom}
                            renderMarkdown={renderMarkdownResponse}
                          />

                          {/* Initial Recommendation Suggestions */}
                          {msg.id === "initial-greeting" && messages.length === 1 && !isLoading && (
                            <div className="mt-3 pt-2.5 border-t border-slate-100">
                              <p className="text-[11px] font-medium text-slate-500 mb-2 flex items-center gap-1.5 select-none">
                                <span>✨</span>
                                <span>What would you like to explore?</span>
                              </p>
                              <div className="flex flex-col gap-1.5">
                                {INITIAL_RECOMMENDATIONS.map((rec, rIdx) => (
                                  <button
                                    key={rIdx}
                                    type="button"
                                    onClick={() => handleSendMessage(rec)}
                                    className="w-full text-left text-xs text-slate-700 bg-slate-50/80 hover:bg-blue-50/90 hover:text-[#000080] hover:border-blue-200 border border-slate-200/80 px-3 py-2 rounded-xl transition-all duration-150 flex items-center justify-between group shadow-xs active:scale-[0.99] cursor-pointer"
                                  >
                                    <span className="font-normal">{rec}</span>
                                    <ArrowRight className="w-3 h-3 text-slate-400 group-hover:text-[#000080] group-hover:translate-x-0.5 transition-all flex-shrink-0" />
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}
                          {/* 1. Primary Action Button: Custom Navigation from RAG (including Book Demo) */}
                          {msg.found && (msg.action_url || msg.action_type === "book_demo") && (
                            <div className="mt-3 pt-2.5 border-t border-slate-100">
                              <button
                                type="button"
                                onClick={() => handleNavigation(msg.action_url || "/courses/sap-btp-freshers-course-training")}
                                className="w-full py-2 px-3 bg-gradient-to-r from-[#000080] to-[#1e3a8a] text-white text-xs font-medium rounded-xl hover:from-[#1e3a8a] hover:to-[#2563eb] transition-all flex items-center justify-center gap-1.5 shadow-sm active:scale-[0.98] cursor-pointer"
                              >
                                <span>{msg.action_text || (msg.action_type === "book_demo" ? "Book Demo" : "View Details")}</span>
                                <ArrowRight className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          )}
                          {/* 2. Fallback Specific Course: "View Course →" (if action_url not explicitly provided) */}
                          {msg.found && !msg.action_url && msg.course_slug && msg.course_slug.trim() !== "" && (
                            <div className="mt-3 pt-2.5 border-t border-slate-100">
                              <button
                                type="button"
                                onClick={() => handleNavigation(msg.course_slug!.trim())}
                                className="w-full py-2 px-3 bg-gradient-to-r from-[#000080] to-[#1e3a8a] text-white text-xs font-medium rounded-xl hover:from-[#1e3a8a] hover:to-[#2563eb] transition-all flex items-center justify-center gap-1.5 shadow-sm active:scale-[0.98] cursor-pointer"
                              >
                                <span>View Course</span>
                                <ArrowRight className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          )}
                          {/* 3. Fallback Broad Catalog Courses: "View Courses →" (if action_url not explicitly provided) */}
                          {msg.found && !msg.action_url && (!msg.course_slug || msg.course_slug.trim() === "") && getBroadCatalogUrl(msg) && (
                            <div className="mt-3 pt-2.5 border-t border-slate-100">
                              <button
                                type="button"
                                onClick={() => handleNavigation(getBroadCatalogUrl(msg)!)}
                                className="w-full py-2 px-3 bg-gradient-to-r from-[#000080] to-[#1e3a8a] text-white text-xs font-medium rounded-xl hover:from-[#1e3a8a] hover:to-[#2563eb] transition-all flex items-center justify-center gap-1.5 shadow-sm active:scale-[0.98] cursor-pointer"
                              >
                                <span>View Courses</span>
                                <ArrowRight className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  <span className="text-[10px] text-slate-400 mt-1 px-1">
                    {msg.timestamp}
                  </span>
                </div>
              ))}

              {/* Loading Indicator */}
              {isLoading && (
                <div className="flex items-start gap-2 max-w-[85%]">
                  <div className="flex-shrink-0 w-6 h-6 rounded-md bg-white border border-slate-200/80 shadow-xs flex items-center justify-center p-0.5 mt-0.5">
                    <img src={chatbotLogo} alt="NxGen Assistant" className="w-full h-full object-contain rounded-xs" />
                  </div>
                  <div className="bg-white px-3.5 py-2.5 rounded-2xl rounded-bl-xs border border-slate-200/80 shadow-sm flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-[#000080] animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="w-2 h-2 rounded-full bg-[#000080] animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="w-2 h-2 rounded-full bg-[#000080] animate-bounce" style={{ animationDelay: "300ms" }} />
                    <span className="text-[11px] text-slate-400 ml-1">Searching...</span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Footer */}
            <div className="p-2.5 bg-white border-t border-slate-100 flex items-center gap-2">
              <input
                ref={inputRef}
                type="text"
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about courses, syllabus, fees..."
                disabled={isLoading}
                aria-label="Ask the chatbot a question"
                className="flex-1 bg-slate-100/80 hover:bg-slate-100 focus:bg-white text-slate-900 text-xs px-3.5 py-2.5 rounded-xl border border-transparent focus:border-[#000080]/30 focus:outline-none focus:ring-2 focus:ring-[#000080]/20 transition-all placeholder:text-slate-400 disabled:opacity-50"
              />
              <button
                type="button"
                onClick={() => handleSendMessage()}
                disabled={!inputQuery.trim() || isLoading}
                aria-label="Send message"
                className="w-9 h-9 rounded-xl bg-gradient-to-r from-[#000080] to-[#1e3a8a] hover:from-[#1e3a8a] hover:to-[#2563eb] text-white flex items-center justify-center shadow-sm disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-95 flex-shrink-0"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* ───────────────────────────────────────────────────────────── */}
      {/* FLOATING CHATBOT LAUNCHER (CUTOUT MASCOT + SPEECH BUBBLE) */}
      {/* ───────────────────────────────────────────────────────────── */}
      {!isOpen && (
        <div className="pointer-events-auto flex flex-col items-end select-none">
          {/* Floating Speech Bubble Callout */}
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.3 }}
            onClick={() => setIsOpen(true)}
            className="mb-1.5 relative cursor-pointer group"
          >
            <div className="bg-white text-slate-800 text-xs font-semibold px-3.5 py-2 rounded-xl shadow-lg border-2 border-[#000080] group-hover:border-[#2563eb] group-hover:text-[#000080] transition-all flex items-center gap-1.5 whitespace-nowrap">
              <span>How can I help you?</span>
            </div>
            {/* Speech bubble pointer arrow */}
            <div className="absolute -bottom-2 right-7 w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[8px] border-t-[#000080]" />
            <div className="absolute -bottom-[5.5px] right-7 w-0 h-0 border-l-[5px] border-l-transparent border-r-[5px] border-r-transparent border-t-[7px] border-t-white" />
          </motion.div>

          {/* Floating Standalone Mascot Button */}
          <motion.button
            type="button"
            onClick={() => setIsOpen(true)}
            aria-label="Open NxGen Assistant"
            title="Chat with NxGen Assistant"
            animate={{
              y: [0, -8, 0],
            }}
            transition={{
              y: {
                duration: 2.4,
                repeat: Infinity,
                ease: "easeInOut",
              },
            }}
            whileHover={{ scale: 1.1, y: -4 }}
            whileTap={{ scale: 0.94 }}
            className="relative flex items-center justify-center bg-transparent border-none shadow-none cursor-pointer p-0 focus:outline-none group"
          >
            {/* Glowing cyan pulse aura */}
            <span className="absolute inset-4 rounded-full bg-cyan-400 opacity-20 animate-ping -z-10 pointer-events-none group-hover:opacity-50" />

            {/* 3D Transparent Robot Mascot */}
            <img
              src={chatbotLogo}
              alt="NxGen Chatbot Assistant"
              className="w-20 h-auto max-sm:w-16 drop-shadow-[0_8px_18px_rgba(0,0,128,0.32)] transition-all duration-300 group-hover:drop-shadow-[0_0_24px_rgba(6,182,212,0.85)] group-hover:brightness-110"
            />
          </motion.button>
        </div>
      )}
    </aside>
  );
};

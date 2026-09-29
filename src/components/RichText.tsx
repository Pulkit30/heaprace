import { Fragment } from "react";

/** Renders the light markdown used in problem descriptions: blank-line paragraphs, `code` and **bold**. */
export default function RichText({ text }: { text: string }) {
  return (
    <div className="prose-problem">
      {text.split(/\n\s*\n/).map((para, i) => (
        <p key={i}>
          {para.split(/(`[^`]+`|\*\*[^*]+\*\*)/).map((part, j) => {
            if (part.startsWith("`") && part.endsWith("`")) return <code key={j}>{part.slice(1, -1)}</code>;
            if (part.startsWith("**") && part.endsWith("**")) return <strong key={j}>{part.slice(2, -2)}</strong>;
            return <Fragment key={j}>{part}</Fragment>;
          })}
        </p>
      ))}
    </div>
  );
}

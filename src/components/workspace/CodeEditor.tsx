"use client";

import Editor, { type BeforeMount, type OnMount } from "@monaco-editor/react";
import { useRef, useState } from "react";
import { loadCode, saveCode } from "@/lib/progress";
import EditorPlaceholder from "./EditorPlaceholder";

export type EditorInstance = Parameters<OnMount>[0];

interface Props {
  slug: string;
  starterCode: string;
  onMount: (editor: EditorInstance, monaco: Parameters<OnMount>[1]) => void;
}

const defineTheme: BeforeMount = (monaco) => {
  monaco.editor.defineTheme("heaprace", {
    base: "vs-dark",
    inherit: true,
    rules: [],
    colors: {
      "editor.background": "#14171f",
      "editor.lineHighlightBackground": "#1b1f29",
      "editorLineNumber.foreground": "#4a5163",
      "editorLineNumber.activeForeground": "#8b93a7",
    },
  });
};

/** Client-only (loaded with ssr: false), so it can read the saved draft from localStorage on first render. */
export default function CodeEditor({ slug, starterCode, onMount }: Props) {
  const [initialCode] = useState(() => loadCode(slug) ?? starterCode);
  const saveTimer = useRef<ReturnType<typeof setTimeout>>(undefined);

  return (
    <Editor
      language="python"
      theme="heaprace"
      defaultValue={initialCode}
      beforeMount={defineTheme}
      onMount={onMount}
      onChange={(value) => {
        clearTimeout(saveTimer.current);
        saveTimer.current = setTimeout(() => saveCode(slug, value ?? ""), 400);
      }}
      loading={<EditorPlaceholder />}
      options={{
        fontSize: 14,
        fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        tabSize: 4,
        automaticLayout: true,
        padding: { top: 12 },
        renderLineHighlight: "line",
      }}
    />
  );
}

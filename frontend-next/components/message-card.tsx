"use client";

import {
  Bot,
  User,
  Sparkles,
} from "lucide-react";

import SqlTable from "./sql-table";

interface Message {
  role: "user" | "assistant";

  content: string;

  provider?: string;

  sql?: string;

  rows?: any[];

  columns?: string[];
}

interface Props {
  message: Message;
}

export default function MessageCard({
  message,
}: Props) {

  const isUser =
    message.role === "user";

  return (
    <div
      className={`
        message-animation
        flex
        w-full

        ${
          isUser
            ? "justify-end"
            : "justify-start"
        }
      `}
    >

      <div
        className={`
          relative
          max-w-[90%]
          overflow-hidden
          rounded-3xl
          border
          p-6
          shadow-2xl
          backdrop-blur-xl

          ${
            isUser
              ? `
                border-blue-500/20
                bg-blue-600/10
              `
              : `
                border-white/10
                bg-slate-900/60
              `
          }
        `}
      >

        {/* GLOW */}

        <div
          className={`
            absolute
            inset-0
            opacity-40

            ${
              isUser
                ? `
                  bg-gradient-to-br
                  from-blue-500/5
                  to-cyan-500/5
                `
                : `
                  bg-gradient-to-br
                  from-white/[0.02]
                  to-white/[0.01]
                `
            }
          `}
        />

        {/* HEADER */}

        <div
          className="
            relative
            mb-5
            flex
            items-center
            gap-4
          "
        >

          {/* ICON */}

          <div
            className={`
              flex
              h-12
              w-12
              items-center
              justify-center
              rounded-2xl
              border

              ${
                isUser
                  ? `
                    border-blue-400/20
                    bg-blue-500/15
                    text-blue-300
                  `
                  : `
                    border-white/10
                    bg-white/[0.03]
                    text-white
                  `
              }
            `}
          >

            {isUser ? (
              <User className="h-5 w-5" />
            ) : (
              <Bot className="h-5 w-5" />
            )}

          </div>

          {/* TITLE */}

          <div>

            <div
              className="
                text-sm
                font-bold
                text-white
              "
            >
              {isUser
                ? "You"
                : "QBS AI Assistant"}
            </div>

            {!isUser && message.provider && (

              <div
                className="
                  mt-1
                  flex
                  items-center
                  gap-2
                  text-xs
                  text-slate-400
                "
              >

                <Sparkles className="h-3 w-3" />

                {message.provider.toUpperCase()}

              </div>

            )}

          </div>

        </div>

        {/* CONTENT */}

        <div
          className="
            relative
            whitespace-pre-wrap
            text-[15px]
            leading-8
            text-slate-100
          "
        >
          {message.content}
        </div>

        {/* SQL */}

        {!isUser && message.sql && (

          <div className="relative mt-6">

            <div
              className="
                mb-3
                text-xs
                font-semibold
                uppercase
                tracking-wider
                text-slate-400
              "
            >
              Generated SQL
            </div>

            <div
              className="
                overflow-x-auto
                rounded-2xl
                border
                border-white/10
                bg-black/40
                p-5
                text-sm
                text-blue-200
              "
            >

              <pre className="whitespace-pre-wrap">
                {message.sql}
              </pre>

            </div>

          </div>

        )}

        {/* TABLE */}

        {!isUser &&
          message.rows &&
          message.rows.length > 0 && (

          <div className="relative">

            <SqlTable rows={message.rows} />

          </div>

        )}

      </div>

    </div>
  );
}
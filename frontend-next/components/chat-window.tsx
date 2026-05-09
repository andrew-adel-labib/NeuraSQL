"use client";

import { useEffect, useRef, useState } from "react";

import {
  ArrowUp,
  Loader2,
  Trash2,
} from "lucide-react";

import MessageCard from "./message-card";
import VoiceInput from "./voice-input";

import { askQuestion } from "@/lib/api";

interface Props {
  provider: string;
}

interface Message {
  role: "user" | "assistant";

  content: string;

  provider?: string;

  sql?: string;

  rows?: any[];

  columns?: string[];
}

export default function ChatWindow({
  provider,
}: Props) {

  const bottomRef =
    useRef<HTMLDivElement | null>(
      null
    );

  const [question, setQuestion] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [messages, setMessages] =
    useState<Message[]>([
      {
        role: "assistant",
        provider,
        content:
          "Welcome to QBS AI Analytics. Ask anything about your ERP database, workshop operations, revenue, inventory, sales, or business performance.",
      },
    ]);

  useEffect(() => {

    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });

  }, [messages, loading]);

  const sendMessage =
    async () => {

      if (
        !question.trim() ||
        loading
      ) {
        return;
      }

      const currentQuestion =
        question;

      setQuestion("");

      const userMessage: Message = {
        role: "user",
        content: currentQuestion,
      };

      setMessages((prev) => [
        ...prev,
        userMessage,
      ]);

      setLoading(true);

      try {

        const response =
          await askQuestion(
            currentQuestion,
            provider
          );

        const assistantMessage: Message =
          {
            role: "assistant",

            content:
              response.summary ||
              "No response returned.",

            provider,

            sql: response.sql,

            rows:
              response.rows || [],

            columns:
              response.columns || [],
          };

        setMessages((prev) => [
          ...prev,
          assistantMessage,
        ]);

      } catch (error: any) {

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            provider,
            content:
              error?.message ||
              "Backend request failed.",
          },
        ]);

      } finally {

        setLoading(false);

      }

    };

  return (
    <div className="flex h-full flex-col">

      {/* TOP BAR */}

      <div
        className="
          flex
          items-center
          justify-end
          px-8
          pt-6
        "
      >

        <button
          onClick={() =>
            setMessages([
              {
                role: "assistant",
                provider,
                content:
                  "Conversation cleared. Ask a new business question.",
              },
            ])
          }
          className="
            flex
            items-center
            gap-2
            rounded-2xl
            border
            border-red-500/20
            bg-red-500/10
            px-4
            py-2.5
            text-sm
            font-medium
            text-red-300
            transition-all
            duration-300

            hover:bg-red-500/20
            hover:text-red-200
          "
        >

          <Trash2 className="h-4 w-4" />

          Clear Conversation

        </button>

      </div>

      {/* MESSAGES */}

      <div
        className="
          chat-scroll
          flex-1
          overflow-y-auto
          px-8
          py-8
        "
      >

        <div
          className="
            mx-auto
            flex
            w-full
            max-w-6xl
            flex-col
            gap-6
          "
        >

          {messages.map(
            (
              message,
              index
            ) => (

              <MessageCard
                key={index}
                message={message}
              />

            )
          )}

          {/* LOADING */}

          {loading && (

            <div className="flex">

              <div
                className="
                  glass
                  flex
                  items-center
                  gap-4
                  rounded-3xl
                  border
                  border-white/10
                  px-6
                  py-5
                "
              >

                <Loader2
                  className="
                    h-5
                    w-5
                    animate-spin
                    text-blue-400
                  "
                />

                <div
                  className="
                    text-sm
                    text-slate-300
                  "
                >
                  Generating enterprise insights...
                </div>

              </div>

            </div>

          )}

          <div ref={bottomRef} />

        </div>

      </div>

      {/* INPUT */}

      <div
        className="
          border-t
          border-white/10
          bg-black/20
          px-8
          py-6
          backdrop-blur-2xl
        "
      >

        <div className="mx-auto max-w-5xl">

          <div
            className="
              glass
              relative
              rounded-[2rem]
              border
              border-white/10
              p-3
            "
          >

            <textarea
              value={question}
              onChange={(e) =>
                setQuestion(
                  e.target.value
                )
              }
              onKeyDown={(e) => {

                if (
                  e.key === "Enter" &&
                  !e.shiftKey
                ) {

                  e.preventDefault();

                  sendMessage();

                }

              }}
              rows={1}
              placeholder="
Ask anything about your ERP data..."
              className="
                w-full
                resize-none
                bg-transparent
                px-5
                py-4
                pr-32
                text-[15px]
                leading-7
                text-white
                outline-none
                placeholder:text-slate-500
              "
            />

            {/* VOICE */}

            <VoiceInput
              setQuestion={
                setQuestion
              }
            />

            {/* SEND */}

            <button
              onClick={sendMessage}
              disabled={
                loading ||
                !question.trim()
              }
              className={`
                absolute
                bottom-3
                right-16
                flex
                h-12
                w-12
                items-center
                justify-center
                rounded-2xl
                transition-all
                duration-300

                ${
                  loading ||
                  !question.trim()
                    ? `
                      cursor-not-allowed
                      bg-slate-800
                      text-slate-500
                    `
                    : `
                      bg-blue-600
                      text-white

                      hover:bg-blue-500
                      hover:shadow-xl
                      hover:shadow-blue-500/20
                    `
                }
              `}
            >

              <ArrowUp className="h-5 w-5" />

            </button>

          </div>

        </div>

      </div>

    </div>
  );
}
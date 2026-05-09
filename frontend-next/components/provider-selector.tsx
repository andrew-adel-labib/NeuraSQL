"use client";

import { Brain, Bot, Sparkles } from "lucide-react";

interface Props {
  provider: string;
  setProvider: (provider: string) => void;
}

const providers = [
  {
    id: "claude",
    label: "Claude",
    icon: Brain,
    description: "Anthropic Intelligence",
  },
  {
    id: "openai",
    label: "OpenAI",
    icon: Sparkles,
    description: "GPT Enterprise Models",
  },
  {
    id: "groq",
    label: "Groq",
    icon: Bot,
    description: "Ultra-fast Open Models",
  },
];

export default function ProviderSelector({
  provider,
  setProvider,
}: Props) {
  return (
    <div className="space-y-4">

      <div>

        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
          AI Provider
        </h2>

        <p className="mt-1 text-xs text-slate-500">
          Select the intelligence engine
        </p>

      </div>

      <div className="space-y-3">

        {providers.map((item) => {
          const Icon = item.icon;

          const active = provider === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setProvider(item.id)}
              className={`
                group
                relative
                w-full
                overflow-hidden
                rounded-2xl
                border
                p-4
                text-left
                transition-all
                duration-300
                backdrop-blur-xl

                ${
                  active
                    ? `
                      border-blue-500/50
                      bg-blue-600/20
                      shadow-lg
                      shadow-blue-500/10
                    `
                    : `
                      border-white/10
                      bg-white/[0.03]
                      hover:border-blue-400/30
                      hover:bg-white/[0.05]
                    `
                }
              `}
            >

              {/* Glow */}

              {active && (
                <div
                  className="
                    absolute
                    inset-0
                    bg-gradient-to-r
                    from-blue-500/10
                    to-cyan-500/10
                  "
                />
              )}

              <div className="relative flex items-start gap-4">

                {/* ICON */}

                <div
                  className={`
                    flex
                    h-11
                    w-11
                    items-center
                    justify-center
                    rounded-xl
                    border

                    ${
                      active
                        ? `
                          border-blue-400/30
                          bg-blue-500/20
                          text-white
                        `
                        : `
                          border-white/10
                          bg-slate-900/60
                          text-slate-300
                        `
                    }
                  `}
                >
                  <Icon className="h-5 w-5" />
                </div>

                {/* CONTENT */}

                <div className="flex-1">

                  <div className="flex items-center justify-between">

                    <h3
                      className={`
                        text-sm
                        font-semibold

                        ${
                          active
                            ? "text-white"
                            : "text-slate-200"
                        }
                      `}
                    >
                      {item.label}
                    </h3>

                    {/* ACTIVE DOT */}

                    <div
                      className={`
                        h-2.5
                        w-2.5
                        rounded-full

                        ${
                          active
                            ? "bg-blue-400 shadow-lg shadow-blue-400/60"
                            : "bg-slate-600"
                        }
                      `}
                    />

                  </div>

                  <p
                    className={`
                      mt-1
                      text-xs
                      leading-5

                      ${
                        active
                          ? "text-blue-100/80"
                          : "text-slate-400"
                      }
                    `}
                  >
                    {item.description}
                  </p>

                </div>

              </div>

            </button>
          );
        })}

      </div>

    </div>
  );
}
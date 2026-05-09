"use client";

import { useEffect, useRef, useState } from "react";

import {
  Loader2,
  Mic,
  MicOff,
} from "lucide-react";

interface Props {
  setQuestion: (
    text: string
  ) => void;
}

export default function VoiceInput({
  setQuestion,
}: Props) {

  const recognitionRef =
    useRef<any>(null);

  const [recording, setRecording] =
    useState(false);

  const [supported, setSupported] =
    useState(true);

  useEffect(() => {

    if (
      typeof window === "undefined"
    ) {
      return;
    }

    const SpeechRecognition =
      (window as any)
        .SpeechRecognition ||
      (window as any)
        .webkitSpeechRecognition;

    if (!SpeechRecognition) {

      setSupported(false);

      return;
    }

    const recognition =
      new SpeechRecognition();

    recognition.lang = "en-US";

    recognition.continuous = false;

    recognition.interimResults = true;

    recognition.maxAlternatives = 1;

    recognition.onstart = () => {

      setRecording(true);

    };

    recognition.onend = () => {

      setRecording(false);

    };

    recognition.onerror = () => {

      setRecording(false);

    };

    recognition.onresult = (
      event: any
    ) => {

      let transcript = "";

      for (
        let i = 0;
        i < event.results.length;
        i++
      ) {

        transcript +=
          event.results[i][0]
            .transcript;

      }

      setQuestion(
        transcript
      );

    };

    recognitionRef.current =
      recognition;

  }, [setQuestion]);

  const toggleRecording = () => {

    if (
      !recognitionRef.current
    ) {
      return;
    }

    if (recording) {

      recognitionRef.current.stop();

      return;
    }

    recognitionRef.current.start();

  };

  if (!supported) {

    return null;

  }

  return (
    <button
      type="button"
      onClick={toggleRecording}
      className={`
        absolute
        right-3
        top-1/2
        flex
        h-12
        w-12
        -translate-y-1/2
        items-center
        justify-center
        rounded-2xl
        border
        transition-all
        duration-300

        ${
          recording
            ? `
              pulse-ring
              border-red-500/30
              bg-red-500/20
              text-red-300
            `
            : `
              border-white/10
              bg-white/[0.04]
              text-slate-300

              hover:border-blue-500/30
              hover:bg-blue-500/10
              hover:text-blue-300
            `
        }
      `}
    >

      {recording ? (

        <Loader2 className="h-5 w-5 animate-spin" />

      ) : (

        <Mic className="h-5 w-5" />

      )}

    </button>
  );
}
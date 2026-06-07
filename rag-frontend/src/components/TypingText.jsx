import { useState, useEffect } from "react";

function TypingText({ text = "", speed = 25 }) {
  const [displayedText, setDisplayedText] =
    useState("");

  useEffect(() => {

    // Prevent crash if text is undefined/null
    if (!text) {
      setDisplayedText("");
      return;
    }

    let index = 0;

    setDisplayedText("");

    const interval = setInterval(() => {

      if (index < text.length) {

        setDisplayedText(
          (prev) => prev + text.charAt(index)
        );

        index++;

      } else {

        clearInterval(interval);

      }

    }, speed);

    return () => clearInterval(interval);

  }, [text, speed]);

  return <p>{displayedText}</p>;
}

export default TypingText;
import { useState, useEffect } from "react";

function TypingText({ text, speed = 25 }) {

  const [displayedText, setDisplayedText] =
    useState("");

  useEffect(() => {

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
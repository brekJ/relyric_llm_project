import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";

const BACKEND_URL = "http://192.168.0.61:5000";

const LoadingSpinner = () => (
  <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
    <circle
      className="opacity-25"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="4"
      fill="none"
    />
    <path
      className="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
    />
  </svg>
);

const compareLyrics = (input, output) => {
  const inputLines = input.split("\n");
  const outputLines = output.split("\n");

  let result = [];

  for (let i = 0; i < Math.max(inputLines.length, outputLines.length); i++) {
    const inputWords = (inputLines[i] || "").split(/(\s+)/);
    const outputWords = (outputLines[i] || "").split(/(\s+)/);

    for (let j = 0; j < Math.max(inputWords.length, outputWords.length); j++) {
      const inputWord = inputWords[j] || "";
      const outputWord = outputWords[j] || "";

      if (inputWord !== outputWord) {
        result.push({ text: outputWord, isDifferent: true });
      } else {
        result.push({ text: outputWord, isDifferent: false });
      }
    }

    if (i < Math.max(inputLines.length, outputLines.length) - 1) {
      result.push({ text: "\n", isDifferent: false });
    }
  }

  return result;
};

const Main = () => {
  const [inputLyrics, setInputLyrics] = useState("");
  const [atmosphere, setAtmosphere] = useState("");
  const [outputLyrics, setOutputLyrics] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [comparedLyrics, setComparedLyrics] = useState([]);
  const outputRef = useRef(null);

  const handleInputChange = (e) => {
    setInputLyrics(e.target.value);
  };

  const handleAtmosphereChange = (e) => {
    setAtmosphere(e.target.value);
  };

  const applyFormattingFromInput = (outputText) => {
    const inputLines = inputLyrics.split("\n");
    const outputWords = outputText.split(/\s+/);

    let result = "";
    let outputIndex = 0;

    for (let i = 0; i < inputLines.length; i++) {
      const inputWords = inputLines[i].split(/\s+/);
      let lineResult = "";

      for (
        let j = 0;
        j < inputWords.length && outputIndex < outputWords.length;
        j++
      ) {
        lineResult += outputWords[outputIndex] + " ";
        outputIndex++;
      }

      result += lineResult.trim() + "\n";
    }

    // 남은 출력 단어들 추가
    while (outputIndex < outputWords.length) {
      result += outputWords[outputIndex] + " ";
      outputIndex++;
    }

    return result.trim();
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setError("");
    setOutputLyrics("");
    setComparedLyrics([]);

    try {
      const response = await fetch(`${BACKEND_URL}/api/ollama`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ input: inputLyrics, atmosphere }),
      });

      if (response.ok) {
        const result = await response.text();
        const formattedLyrics = applyFormattingFromInput(result);
        setOutputLyrics(formattedLyrics);
        setComparedLyrics(compareLyrics(inputLyrics, formattedLyrics));
      } else {
        throw new Error("Server responded with an error");
      }
    } catch (err) {
      console.error("Error:", err);
      setError(`Error processing lyrics: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [outputLyrics]);

  return (
    <div className="min-h-screen bg-purple-200 p-8 flex flex-col items-center justify-center">
      <div className="w-full max-w-4xl flex flex-col items-center">
        <div className="w-full flex flex-col md:flex-row gap-8 mb-6">
          <motion.div
            className="flex-1 flex flex-col"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h2 className="text-2xl font-bold mb-4 text-purple-800">
              Input Lyrics
            </h2>
            <textarea
              className="w-full h-64 p-4 bg-black text-white rounded-lg resize-none shadow-inner mb-4"
              value={inputLyrics}
              onChange={handleInputChange}
              placeholder="Enter your lyrics here..."
            />
            <h2 className="text-2xl font-bold mb-4 text-purple-800">
              Atmosphere
            </h2>
            <textarea
              className="w-full h-16 p-4 bg-black text-white rounded-lg resize-none shadow-inner"
              value={atmosphere}
              onChange={handleAtmosphereChange}
              placeholder="Describe the atmosphere..."
            />
          </motion.div>

          <motion.div
            className="flex-1 flex flex-col"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h2 className="text-2xl font-bold mb-4 text-purple-800">
              Output Lyrics
            </h2>
            <div
              ref={outputRef}
              className="w-full h-[calc(100%-2rem)] p-4 bg-black text-white rounded-lg overflow-auto shadow-inner whitespace-pre-wrap"
            >
              {comparedLyrics.map((word, index) => (
                <span
                  key={index}
                  className={
                    word.isDifferent ? "font-bold text-yellow-400" : ""
                  }
                >
                  {word.text}
                </span>
              ))}
            </div>
          </motion.div>
        </div>

        {error && <p className="text-red-500 mb-4">{error}</p>}

        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            type: "spring",
            stiffness: 260,
            damping: 20,
            delay: 0.3,
          }}
          whileHover={{ scale: 1.05, transition: { duration: 0.2 } }}
          whileTap={{ scale: 0.95 }}
          onClick={handleSubmit}
          disabled={isLoading}
          className={`bg-purple-600 text-white px-8 py-3 rounded-full text-lg font-semibold 
                     hover:bg-purple-700 transition duration-300 flex items-center justify-center
                     ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          {isLoading ? (
            <>
              <LoadingSpinner />
              Processing...
            </>
          ) : (
            "Process Lyrics"
          )}
        </motion.button>
      </div>
    </div>
  );
};

export default Main;

// Quiz module
const Quiz = (() => {
  let currentQuiz = null;
  let answers = {};
  let questionIndex = 0;
  let startTime = null;

  function renderQuestion(index) {
    if (!currentQuiz) return;
    const q = currentQuiz.questions[index];
    const total = currentQuiz.questions.length;

    document.getElementById("quiz-title").textContent = currentQuiz.title || "Quiz";
    document.getElementById("quiz-progress-bar").style.width = `${((index + 1) / total) * 100}%`;
    document.getElementById("quiz-counter").textContent = `Question ${index + 1} / ${total}`;
    document.getElementById("question-text").textContent = q.question;

    const optCont = document.getElementById("options-container");
    optCont.innerHTML = "";
    const letters = ["A", "B", "C", "D"];

    q.options.forEach((opt, i) => {
      const div = document.createElement("div");
      div.className = "quiz-option" + (answers[index] === i ? " selected" : "");
      div.dataset.index = i;
      div.innerHTML = `
        <span class="quiz-letter">${letters[i]}</span>
        <span>${opt}</span>
      `;
      div.addEventListener("click", () => selectOption(index, i));
      optCont.appendChild(div);
    });

    document.getElementById("prev-btn").disabled = index === 0;
    document.getElementById("next-btn").textContent = index === total - 1 ? "Submit Quiz" : "Next";
  }

  function selectOption(qIndex, optIndex) {
    answers[qIndex] = optIndex;
    document.querySelectorAll(".quiz-option").forEach(el => el.classList.remove("selected"));
    document.querySelectorAll(".quiz-option")[optIndex]?.classList.add("selected");
  }

  function loadQuiz(quizData) {
    currentQuiz = quizData;
    answers = {};
    questionIndex = 0;
    startTime = Date.now();
    renderQuestion(0);
    document.getElementById("quiz-container").style.display = "block";
    document.getElementById("quiz-loader").style.display = "none";
  }

  async function submitQuiz(quizId) {
    const timeSec = Math.round((Date.now() - startTime) / 1000);
    const strAnswers = {};
    Object.keys(answers).forEach(k => { strAnswers[k.toString()] = answers[k]; });

    try {
      const result = await DentAI.apiFetch("/api/quiz/submit", {
        method: "POST",
        body: JSON.stringify({ quiz_id: quizId, answers: strAnswers, time_taken_sec: timeSec }),
      });
      showResults(result);
    } catch (e) {
      alert("Failed to submit quiz: " + e.message);
    }
  }

  function showResults(attempt) {
    const pct = attempt.score;
    const grade = pct >= 90 ? "Excellent!" : pct >= 70 ? "Good Job!" : pct >= 50 ? "Keep Practicing!" : "Needs Improvement";
    const color = pct >= 70 ? "#28a745" : pct >= 50 ? "#ffc107" : "#dc3545";

    document.getElementById("quiz-container").innerHTML = `
      <div style="text-align:center; padding: 2rem;">
        <div style="font-size:4rem;">🎯</div>
        <h2 style="margin: 1rem 0; color: ${color};">${pct}%</h2>
        <p style="font-size:1.3rem; font-weight:600;">${grade}</p>
        <p class="text-muted" style="margin-top:0.5rem;">
          Completed in ${Math.floor(attempt.time_taken_sec / 60)}m ${attempt.time_taken_sec % 60}s
        </p>
        <div style="display:flex; justify-content:center; gap:1rem; margin-top:2rem;">
          <a href="/student" class="btn btn-outline">Back to Dashboard</a>
          <button onclick="location.reload()" class="btn btn-primary">Try Again</button>
        </div>
      </div>
    `;
  }

  function init(quizData) {
    if (quizData) {
      loadQuiz(quizData);
    }

    document.getElementById("next-btn")?.addEventListener("click", () => {
      const total = currentQuiz?.questions.length || 0;
      if (questionIndex < total - 1) {
        questionIndex++;
        renderQuestion(questionIndex);
      } else {
        submitQuiz(currentQuiz.id || 0);
      }
    });

    document.getElementById("prev-btn")?.addEventListener("click", () => {
      if (questionIndex > 0) {
        questionIndex--;
        renderQuestion(questionIndex);
      }
    });
  }

  return { init, loadQuiz };
})();

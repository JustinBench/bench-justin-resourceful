const questionsSection = document.querySelector('#question-container');
const resultSection = document.getElementById('result-container');
const loadWarning = document.querySelector('.load-text');
const loadImg = document.querySelector('.load-logo');
const correctText = document.getElementById('correct-answers');
const totalQuestions = document.getElementById('total-questions');
const zeroScoreImage = document.getElementById('zero-score-image');
const perfectScoreImage = document.getElementById('perfect-score-image');
const start_quiz_form = document.getElementById('question-amount-form');
let zeldaQuestions = [];
let currentQuestion = 0;
let correctAnswers = 0;

function shuffle(array) {
  const shuffled = [...array]; // copy it doesn't mutate the original
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]; // swap
  }
  return shuffled;
}

function createQuestion(questionObj, questionNum, totalQuestions) {
    const newQuestionSection = document.createElement('section');
    newQuestionSection.classList.add('hidden','question');

    const questionContext = document.createElement('div');
    questionContext.classList.add('question-context');

    const gameLabel = document.createElement('span');
    gameLabel.classList.add('game-label');
    gameLabel.textContent = questionObj.game || 'Misc';

    const imageName = typeof questionObj.img === 'string' && questionObj.img.trim()
        ? questionObj.img.trim().split(/[\\/]/).pop()
        : 'hestus_gift.png';
    const imageFilename = imageName.includes('.') ? imageName : `${imageName}.png`;
    const questionImage = document.createElement('img');
    questionImage.classList.add('question-image');
    questionImage.src = `/static/media/${encodeURIComponent(imageFilename)}`;
    questionImage.alt = `${gameLabel.textContent} associated image`;
    questionImage.addEventListener('error', () => {
        questionImage.src = '/static/media/hestus_gift.png';
    }, { once: true });

    const questionHeader = document.createElement('h4');
    questionHeader.textContent = `Question ${questionNum}/${totalQuestions}:`
    questionHeader.classList.add('question-header');

    const questionText = document.createElement('p');
    questionText.textContent = `${decodeHTML(questionObj.question)}`;

    let possibleAnswers = [questionObj.correct_answer, ...questionObj.incorrect_answers];
    shuffledAnswers = shuffle(possibleAnswers);

    const answersList = document.createElement('ul');
    answersList.classList.add('answers-list');

    let labels = ['A', 'B', 'C', 'D']
    shuffledAnswers.forEach((answer, index, shuffledAnswers)  => {
        const li = document.createElement('li');
        
        const button = document.createElement('button');
        button.classList.add('answer-button');
        button.dataset.isCorrect = (answer === questionObj.correct_answer);

        button.append(`${labels[index]}`);

        const answerSpan = document.createElement('span');
        answerSpan.classList.add('answer-text');
        answerSpan.textContent = decodeHTML(answer);
        button.addEventListener('click', handleAnswerClick);

        li.appendChild(button);
        li.appendChild(answerSpan);
        answersList.appendChild(li);
    });

    questionContext.appendChild(questionImage);
    questionContext.appendChild(gameLabel);
    newQuestionSection.appendChild(questionContext);
    newQuestionSection.appendChild(questionHeader);
    newQuestionSection.appendChild(questionText);
    newQuestionSection.appendChild(answersList);
    zeldaQuestions.push(newQuestionSection);
    questionsSection.appendChild(newQuestionSection);
}

function createReviewQuestion(questionObj) {
    const reviewSection = document.querySelector('.review-questions');
    if (!reviewSection) return;

    const newReviewQuestion = document.createElement('section');
    newReviewQuestion.classList.add('review-question');

    const questionContext = document.createElement('div');
    questionContext.classList.add('question-context');

    const gameLabel = document.createElement('span');
    gameLabel.classList.add('game-label');
    gameLabel.textContent = questionObj.game || 'Misc';

    const imageName = typeof questionObj.img === 'string' && questionObj.img.trim()
        ? questionObj.img.trim().split(/[\\/]/).pop()
        : 'hestus_gift.png';
    const imageFilename = imageName.includes('.') ? imageName : `${imageName}.png`;
    const questionImage = document.createElement('img');
    questionImage.classList.add('question-image');
    questionImage.src = `/static/media/${encodeURIComponent(imageFilename)}`;
    questionImage.alt = `${gameLabel.textContent} associated image`;
    questionImage.addEventListener('error', () => {
        questionImage.src = '/static/media/hestus_gift.png';
    }, { once: true });

    const questionText = document.createElement('p');
    questionText.textContent = decodeHTML(questionObj.question);

    const answersList = document.createElement('ul');
    answersList.classList.add('review-answers-list');

    const answers = [
        { text: questionObj.correct_answer, correct: true },
        ...(questionObj.incorrect_answers || []).map(answer => ({ text: answer, correct: false }))
    ];
    answers.forEach(answer => {
        const li = document.createElement('li');
        li.classList.add(answer.correct ? 'review-correct-answer' : 'review-incorrect-answer');
        li.textContent = `${answer.correct ? 'Correct: ' : 'Incorrect: '}${decodeHTML(answer.text)}`;
        answersList.appendChild(li);
    });

    const editButton = document.createElement('button');
    editButton.type = 'button';
    editButton.classList.add('edit-question-button');
    editButton.textContent = 'Edit question';
    editButton.setAttribute('aria-label', `Edit question ${questionObj.id}`);

    questionContext.appendChild(questionImage);
    questionContext.appendChild(gameLabel);
    newReviewQuestion.appendChild(questionContext);
    newReviewQuestion.appendChild(questionText);
    newReviewQuestion.appendChild(answersList);
    newReviewQuestion.appendChild(editButton);
    reviewSection.appendChild(newReviewQuestion);
}

async function loadReviewQuestions() {
    const reviewSection = document.querySelector('.review-questions');
    if (!reviewSection) return;

    try {
        const questions = await fetchQuestions();
        reviewSection.replaceChildren();
        questions.forEach(createReviewQuestion);
    } catch (error) {
        console.error('Unable to load review questions:', error);
        reviewSection.textContent = 'Unable to load questions right now.';
    }
}

loadReviewQuestions();

function handleAnswerClick(event) {
    const clickedButton = event.currentTarget;
    const answerLists = document.querySelectorAll('.answers-list');
    if (clickedButton.dataset.isCorrect === "true") {
        correctAnswers++;
    }
    nextQuestion();
}

function showResults() {
    correctText.textContent = correctAnswers;
    totalQuestions.textContent = zeldaQuestions.length;
    zeroScoreImage.classList.toggle('hidden', correctAnswers !== 0);
    perfectScoreImage.classList.toggle(
        'hidden',
        zeldaQuestions.length === 0 || correctAnswers !== zeldaQuestions.length
    );
    resultSection.classList.remove('hidden');
    const refreshPageButton = document.getElementById('refresh-page-button');
    refreshPageButton.classList.remove('hidden');
    refreshPageButton.addEventListener('click', () => window.location.reload());
}

function decodeHTML(str) {
  const txt = document.createElement('textarea');
  txt.innerHTML = str;
  return txt.value;
}

async function fetchQuestions() {
    const response = await fetch("/questions_and_answers");

    if (!response.ok) {
        throw new Error(`The server returned ${response.status}`);
    }

    return await response.json();
}

async function selectQuestionIds(requestAmount) {
    const questions = await fetchQuestions();
    const availableIds = questions.map(question => question.id);

    const amount = requestAmount === 0 ? availableIds.length : Math.min(requestAmount, availableIds.length);

    const selectedIds = [];

    while (selectedIds.length < amount) {
        const randomIndex = Math.floor(Math.random() * availableIds.length);
        selectedIds.push(availableIds.splice(randomIndex, 1)[0]);
    }

    return selectedIds;
}

async function fetchQuestionById(id) {
    const response = await fetch(`/questions-and-answers/${id}`);

    if (!response.ok) {
        throw new Error(`Could not retrieve question ${id}: ${response.status}`)
    }

    return response.json();
}

async function loadLocalQuestions(amount=0) {
    try {
        const ids = await selectQuestionIds(amount);

        for (let index = 0; index < ids.length; index++) {
            const question = await fetchQuestionById(ids[index]);
            createQuestion(question, index + 1, ids.length);
        }

        if (ids.length > 0) {
            showQuestion(currentQuestion);
            start_quiz_form.classList.add('hidden');
        }
    } catch (error) {
        console.error("Unable to load questions:", error);
    }
}

function showQuestion(index) {
    zeldaQuestions[index].classList.remove('hidden');
}

function hideQuestion(index) {
    zeldaQuestions[index].classList.add('hidden');
}

function nextQuestion() {
    hideQuestion(currentQuestion);
    currentQuestion++;
    if (currentQuestion < zeldaQuestions.length) {
        showQuestion(currentQuestion);
    } else {
        showResults();
    }
}

async function submitQuestion(question, correctAnswer, incorrectAnswers, game, uploadedImage) {
    const existingQuestions = await fetchQuestions();
    const normalizedQuestion = question.trim().toLowerCase();

    let message = "";

    const alreadyExists = existingQuestions.some(
        existing => existing.question.trim().toLowerCase() === normalizedQuestion
    );

    if (alreadyExists) {
        message = "That question already exists!"
    } else if (!normalizedQuestion.includes("zelda")) {
        message = 'The question must be about a Zelda game (include the word "Zelda").';
    } else {
        const questionData = new FormData();
        questionData.append("question", question);
        questionData.append("correct_answer", correctAnswer);
        questionData.append("game", game.trim());
        incorrectAnswers.forEach(answer => questionData.append("incorrect_answers", answer));
        if (uploadedImage) {
            questionData.append("image", uploadedImage);
        }

        const response = await fetch("/questions_and_answers", {
            method: "POST",
            body: questionData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `Request failed: ${response.status}`)
        }
        
        message = "Question saved successfully!";
    }

    document.getElementById("add-question-form").reset();
    const result_message = document.getElementById('form-result-message');
    result_message.textContent = message;
    result_message.classList.remove('hidden');
}

const imageInput = document.getElementById('image-input');
const imagePreview = document.getElementById('image-preview');

if (imageInput && imagePreview) {
    let previewUrl;

    imageInput.addEventListener('change', () => {
        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
        }

        const image = imageInput.files[0];
        if (!image) {
            imagePreview.removeAttribute('src');
            imagePreview.classList.add('hidden');
            return;
        }

        previewUrl = URL.createObjectURL(image);
        imagePreview.src = previewUrl;
        imagePreview.classList.remove('hidden');
    });

    document.getElementById('add-question-form').addEventListener('reset', () => {
        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
            previewUrl = undefined;
        }
        imagePreview.removeAttribute('src');
        imagePreview.classList.add('hidden');
    });
}

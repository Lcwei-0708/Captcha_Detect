<template>
    <div class="captcha-detect">
        <h2>驗證碼辨識</h2>
        <div id="main" class="main">
            <form id="uploadForm" @submit.prevent class="uploadForm">
                <label class="custum-file-upload" :class="{ hidden: imgVisible }" @dragover.prevent="handleDragOver"
                    @dragenter.prevent="handleDragEnter" @dragleave.prevent="handleDragLeave"
                    @drop.prevent="handleDrop">
                    <div class="icon">
                        <iconify-icon icon="icon-park-outline:upload-picture"></iconify-icon>
                    </div>
                    <div class="text">
                        <span>拖曳或貼上驗證碼圖片</span>
                    </div>
                    <input type="file" id="file" @change="handleFileChange" ref="fileInput" />
                </label>
            </form>
        </div>
        <div class="result-container" v-if="imgVisible">
            <div class="img-container">
                <img class="input_img" :src="imgSrc" alt="Uploaded Image" />
            </div>
            <button id="resetBtn" @click="resetImage" class="resetBtn">
                重設圖片
            </button>
            <div id="loading" v-if="isLoading" class="loading">
                <div class="spinner"></div>
                <p>辨識中...</p>
            </div>
            <div id="result" v-if="resultVisible" class="result">
                辨識結果：<span id="captcha" class="captcha">{{ captcha }}</span>
                <button class="copy-btn" :class="{ disabled: copyDisabled }" @click="copyCaptcha"
                    :disabled="copyDisabled">
                    <iconify-icon :icon="copyIcon" class="icon"></iconify-icon>
                </button>
            </div>
        </div>

        <div class="test-container">
            <h3>測試用驗證碼</h3>
            <div class="slider">
                <div class="slides">
                    <div class="slide" v-for="(image, index) in testImages" :key="index" @click="handleTestImageClick(image.src)">
                        <img :src="image.src" :alt="image.alt" />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from "vue";

export default {
    name: "CaptchaDetect",
    setup() {
        const testImages = ref([]);

        onMounted(async () => {
            const images = import.meta.glob("@/assets/captcha_*.png");
            const imagePromises = Object.entries(images).map(
                async ([path, importFn]) => {
                    const num = path.match(/captcha_(\d+)\.png/)[1];
                    const module = await importFn();
                    return {
                        src: module.default,
                        alt: `Image ${num}`,
                    };
                }
            );

            const loadedImages = await Promise.all(imagePromises);
            testImages.value = [...loadedImages, ...loadedImages.slice(0, 6)];
        });

        return {
            testImages,
        };
    },
    data() {
        return {
            imgSrc: "",
            imgVisible: false,
            resultVisible: false,
            captcha: "",
            copyDisabled: false,
            copyIcon: "icon-park-outline:copy",
            isLoading: false,
        };
    },
    methods: {
        handleFileChange(event) {
            const file = event.target.files[0];
            if (file) {
                const validImageTypes = ["image/jpeg", "image/png", "image/gif"];
                if (!validImageTypes.includes(file.type)) {
                    alert("請選擇一個有效的圖片檔案 (JPEG, PNG, GIF)");
                    this.$refs.fileInput.value = "";
                    return;
                }
                this.processImage(file);
                this.$refs.fileInput.value = "";
            }
        },
        handleDragOver() {
            // 可添加拖曳中的視覺效果
        },
        handleDragEnter() {
            // 可添加拖曳進入時的視覺效果
        },
        handleDragLeave() {
            // 可移除拖曳離開時的視覺效果
        },
        handleDrop(event) {
            const file = event.dataTransfer.files[0];
            if (file) {
                this.processImage(file);
            }
        },
        displayImage(file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                this.imgSrc = e.target.result;
                this.imgVisible = true;
            };
            reader.readAsDataURL(file);
        },
        async processImage(file) {
            this.displayImage(file);
            this.resultVisible = false;
            this.isLoading = true;
            try {
                const formData = new FormData();
                formData.append("image", file);

                const response = await fetch("https://api.lcwei.site/api/captcha_ocr", {
                    method: "POST",
                    body: formData,
                });

                if (!response.ok) {
                    throw new Error(response.statusText);
                }

                const data = await response.json();

                if (data.error) {
                    throw new Error(data.error);
                }

                this.captcha = data.result;
                this.resultVisible = true;
            } catch (error) {
                console.error("驗證碼辨識過程中發生錯誤:", error);
                this.captcha = "驗證碼偵測失敗";
                this.resultVisible = true;
            } finally {
                this.isLoading = false;
                this.imgVisible = true;
            }
        },
        copyCaptcha() {
            if (this.captcha) {
                navigator.clipboard
                    .writeText(this.captcha)
                    .then(() => {
                        this.copyDisabled = true;
                        this.copyIcon = "tabler:check";
                        setTimeout(() => {
                            this.copyIcon = "icon-park-outline:copy";
                            this.copyDisabled = false;
                        }, 1000);
                    })
                    .catch((err) => {
                        console.error("複製失敗:", err);
                    });
            }
        },
        resetImage() {
            this.imgSrc = "";
            this.imgVisible = false;
            this.captcha = "";
            this.resultVisible = false;
            this.$refs.fileInput.value = "";
        },
        handleKeyDown(event) {
            if (event.ctrlKey && event.key === 'v') {
                event.preventDefault();
                navigator.clipboard.read().then((clipboardItems) => {
                    for (const clipboardItem of clipboardItems) {
                        for (const type of clipboardItem.types) {
                            if (type.startsWith('image/')) {
                                clipboardItem.getType(type).then((blob) => {
                                    const file = new File([blob], "pasted-image.png", { type: blob.type });
                                    this.processImage(file);
                                });
                                return;
                            }
                        }
                    }
                });
            }
        },
        async handleTestImageClick(imageSrc) {
            try {
                const response = await fetch(imageSrc);
                const blob = await response.blob();
                const file = new File([blob], "test-image.png", { type: blob.type });
                this.processImage(file);
            } catch (error) {
                console.error("處理測試圖片時發生錯誤:", error);
            }
        },
    },
    mounted() {
        document.addEventListener('keydown', this.handleKeyDown);
    },
    unmounted() {
        document.removeEventListener('keydown', this.handleKeyDown);
    },
};
</script>

<style scoped>
.captcha-detect {
    text-align: center;
    padding: 20px;
}

.result-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 20px;
}

.img-container {
    margin-bottom: 10px;
}

.input_img {
    height: auto;
    max-width: 300px;
    max-height: 15vh;
    margin-top: 30px;
    border-radius: 0.5rem;
    border: 1px solid var(--font2-color);
}

.resetBtn {
    margin: 10px 0;
    padding: 10px 15px;
    background-color: #cf3c31;
    font-size: 18px;
    color: white;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
}

.captcha {
    margin: 0 10px;
    padding: 10px 20px;
    background-color: var(--bg3-color);
    border-radius: 0.5rem;
}

.copy-btn {
    background-color: #2f953c;
    color: white;
    border: none;
    padding: 10px;
    border-radius: 0.5rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
}

.copy-btn .icon {
    font-size: 20px;
}

.copy-btn.disabled {
    background-color: transparent;
    cursor: default;
    color: var(--font2-color);
}

.result {
    margin-top: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--font-color);
    font-size: 20px;
    gap: 10px;
}

h2 {
    background-color: var(--bg4-color);
    color: var(--font-color);
    margin-top: 80px;
}

h3 {
    color: var(--font-color);
    margin: 0 auto;
    text-align: center;
}

.uploadForm {
    margin: auto;
    user-select: none;
}

.custum-file-upload {
    margin: 5vh auto 0 auto;
    height: 25vh;
    width: 20vw;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 3px dashed var(--border-color);
    background-color: var(--bg2-color);
    padding: 1.5rem;
    border-radius: 15px;
    cursor: pointer;
    gap: 20px;
}

.custum-file-upload .icon {
    display: flex;
    align-items: center;
    justify-content: center;
}

.custum-file-upload .icon {
    font-size: 80px;
    color: var(--font2-color);
}

.custum-file-upload .text {
    display: flex;
    align-items: center;
    justify-content: center;
}

.custum-file-upload .text span {
    font-weight: normal;
    color: var(--font2-color);
}

.custum-file-upload input {
    display: none;
}

.custum-file-upload.hidden {
    display: none;
}

.custum-file-upload.over,
.custum-file-upload:hover {
    border: 3px solid var(--border-color);
    box-shadow: inset var(--shadow4-color);
}

.test-container {
    width: 100%;
    overflow: hidden;
    position: fixed;
    bottom: 20%;
    left: 50%;
    transform: translateX(-50%);
}

.slider {
    margin-top: 5vh;
    width: 100%;
    overflow: hidden;
}

.slides {
    display: flex;
    width: calc(180%);
    /* 使內容寬度為原內容的兩倍，以實現無縫滾動 */
    animation: marquee-animation 20s linear infinite;
    /* 調整時間來控制滾動速度 */
}

.slide {
    flex: 0 0 auto;
    width: 10%;
    cursor: pointer; /* 添加這行以顯示可點擊的效果 */
}

.slide img {
    border-radius: 15px;
    border: 1px solid var(--font-color);
    width: 300px;
    display: block;
}

.loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 20px;
}

.spinner {
    border: 4px solid var(--bg4-color);
    border-top: 4px solid var(--border-color);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

#loading p {
    margin-top: 10px;
    color: var(--font-color);
}

@keyframes marquee-animation {
    0% {
        transform: translateX(0);
    }

    100% {
        transform: translateX(-100%);
        /* 從0滾動到一半，實現無縫效果 */
    }
}

/*--------------------------------------------------------------
# Responsive Layout
--------------------------------------------------------------*/
@media (max-width: 1200px) {
    h2 {
        margin: 0px;
        padding: 20px 50px;
        font-size: 22px;
        position: fixed;
        top: 0px;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        border-bottom: 1px solid var(--border-color);
    }

    .main {
        margin-top: 15vh;
    }

    .custum-file-upload {
        margin: 5vh auto 0 auto;
        height: 20vh;
        width: 80%;
        font-size: 18px;
    }

    .copy-btn {
        font-size: 18px;
    }

    .result {
        font-size: 18px;
    }

    .captcha {
        padding: 10px 15px;
    }

    .slides {
        width: calc(850%);
    }

    .img-container {
        flex-direction: column;
    }
}
</style>
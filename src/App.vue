<template>
  <Header />
  <Captcha_detect />
  <Footer />
</template>

<script>
import Header from './components/header.vue';
import Footer from './components/footer.vue';
import Captcha_detect from './components/captcha_detect.vue';
export default {
  components: {
    Header,
    Captcha_detect,
    Footer
  }
}
</script>

<style>

</style>
<template>
  <div>
    <b-alert
      :show="dismissCountDown"
      variant="success"
      @dismissed="dismissCountDown=0"
      @dismiss-count-down="countDownChanged"
      px-2 py-1
    >
      {{ message }}
    </b-alert>
  </div>
</template>

<script>
export default {
  props: ['message', 'dismissCountDown'],
  methods: {
    countDownChanged (dismissCountDown) {
      this.dismissCountDown = dismissCountDown
    }
  }
}
</script>

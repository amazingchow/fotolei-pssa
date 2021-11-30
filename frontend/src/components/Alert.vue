<template>
  <div>
    <b-alert show>{{ message }}</b-alert>
  </div>
</template>

<script>
export default {
  props: ['message']
}
</script>

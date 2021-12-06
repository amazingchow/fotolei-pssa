<template>
  <div>
    <b-alert variant="success" show dismissible>{{ message }}</b-alert>
  </div>
</template>

<script>
export default {
  props: ['message']
}
</script>

<template>
  <div>
    <b-alert variant="secondary" show dismissible>{{ message }}</b-alert>
  </div>
</template>

<script>
export default {
  props: ['message']
}
</script>

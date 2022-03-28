<template>
  <div class="row">
    <div class="col-sm-12">
      <b-alert variant="secondary" show dismissible>{{ message }}</b-alert>
    </div>
  </div>
</template>

<script>
export default {
  props: ['message']
}
</script>

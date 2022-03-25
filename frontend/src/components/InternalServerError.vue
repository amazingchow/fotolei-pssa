<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-12">
        <center>
          <h1>Internal Server Error!</h1>
          <p><a href="/">Go Home?</a></p>
        </center>
      </div>
    </div>
  </div>
</template>

<style>
center {
  margin: 15vw;
}

h1 {
  color: var(--border);
  font-size: 2em;
}
</style>

<script>
export default {
  name: 'InternalServerError'
}
</script>

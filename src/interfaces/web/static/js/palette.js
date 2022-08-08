$( document ).ready(() => {
  let palette = window.localStorage.getItem('palette')
  if (palette == null) {
    palette = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark-palette' : 'light-palette'
  }
  $('html').addClass((_, currentClass) => {
    if (currentClass.includes('dark-palette') || currentClass.includes('light-palette')) {
      $('html').removeClass(currentClass)
    }
    return palette;
  })

  let lightSwitch = $('#light-switch')
  if (lightSwitch != null) {
    lightSwitch.on('click', () => {
      let target = 'light-palette'
      $('html').addClass((_, currentClass) => {
        if (currentClass.includes(target)) {
          target = 'dark-palette'
        }
        $('html').removeClass(currentClass)
        window.localStorage.setItem('palette', target)
        return target;
      })
    })
  }
})

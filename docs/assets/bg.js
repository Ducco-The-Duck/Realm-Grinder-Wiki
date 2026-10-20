// one of the game's three alignment backgrounds (Good, Evil, Neutral), picked at random on every load
(function () {
  var k = ['good', 'evil', 'neutral'][Math.floor(Math.random() * 3)];
  var d = document.createElement('div');
  d.id = 'bgfx';
  d.style.backgroundImage = 'url(assets/bg/' + k + '.jpg)';
  document.body.insertBefore(d, document.body.firstChild);
})();

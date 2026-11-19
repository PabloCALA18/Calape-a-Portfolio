const EDITANDO = document.body.dataset.editando === "1";
const CSRF = document.querySelector('meta[name="csrf-token"]').content;

// ---------- MODALES ----------
// Abre el modal de una sección: vacío para agregar, o con datos para editar
function abrirModal(seccion, datos = null) {
  const dialogo = document.getElementById("modal-" + seccion);
  const form = dialogo.querySelector("form");
  form.reset();

  if (datos) {
    form.action = `/editar/${seccion}/${datos.id}`;
    for (const [clave, valor] of Object.entries(datos)) {
      const campo = form.elements[clave];
      if (campo && campo.type !== "file") campo.value = valor ?? "";
    }
  } else {
    form.action = `/agregar/${seccion}`;
  }
  dialogo.showModal();
}

// Modal para subir foto, banner o logo
function abrirImagen(campo) {
  const dialogo = document.getElementById("modal-imagen");
  dialogo.querySelector("form").action = `/perfil/imagen/${campo}`;
  dialogo.showModal();
}

// Cerrar un modal haciendo clic afuera
document.querySelectorAll("dialog").forEach(d =>
  d.addEventListener("click", e => { if (e.target === d) d.close(); })
);

// ---------- DRAG AND DROP (solo en modo edición) ----------
if (EDITANDO && window.Sortable) {
  document.querySelectorAll("[data-sortable]").forEach(lista => {
    Sortable.create(lista, {
      animation: 150,
      draggable: "[data-id]",
      onEnd: () => {
        const ids = [...lista.querySelectorAll("[data-id]")].map(el => el.dataset.id);
        fetch(`/ordenar/${lista.dataset.seccion}`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-CSRFToken": CSRF },
          body: JSON.stringify({ ids })
        });
      }
    });
  });
}

// ---------- ANIMACIÓN DE APARICIÓN ----------
// Agrega la clase "visible" cuando el elemento entra en pantalla
const observador = new IntersectionObserver(entradas => {
  entradas.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add("visible");
      observador.unobserve(e.target);
    }
  });
}, { threshold: 0.15 });

document.querySelectorAll(".reveal, .skill").forEach(el => observador.observe(el));


// ---------- MENÚ: resalta la sección que se está viendo ----------
const enlacesMenu = document.querySelectorAll(".menu a");
const observadorMenu = new IntersectionObserver(entradas => {
  entradas.forEach(e => {
    if (e.isIntersecting) {
      enlacesMenu.forEach(a => a.classList.toggle("activo", a.hash === "#" + e.target.id));
    }
  });
}, { rootMargin: "-40% 0px -55% 0px" });

document.querySelectorAll("main section[id]").forEach(s => observadorMenu.observe(s));
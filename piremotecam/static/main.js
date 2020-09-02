/*
Python simple Raspberry-Pi camera module web interface
Copyright (c) 2020 Luiz Eduardo Amaral <luizamaral306@gmail.com>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the copyright holder nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
*/
let delIdx;  // Communicate delete index with this. Ugly but it works :(

function pictureThenDownload() {
  const uri = "/picture"
  const method = "POST"
  const request = new Request(uri, {method})
  fetch(request).then(response => {
    downloadURI("/picture?index=-1&download=true")
    location.reload()
  })
}

function downloadURI(uri) {
  var link = document.createElement("a");
  link.href = uri
  link.target = "_new"
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  delete link
}

function deleteIndex() {
  const uri = "/delete?index=" + parseInt(delIdx)
  const method = "DELETE"
  const request = new Request(uri, {method})
  fetch(request).then(response => {
    location.reload()
  })
}

function deleteAll() {
  const uri = "/deleteAll"
  const method = "DELETE"
  const request = new Request(uri, {method})
  fetch(request).then(response => {
    location.reload()
  })
}

function openModal(id) {
  $('#'+id).modal('show');
}

function addPaginator() {
  const box = paginator({
    table: $("#files")[0],
    rows_per_page: 15,
    page_options: false,
    active_class: "active",
    box_mode: "list",
  });
  box.className = "pagination";
  $(".table-index").append(box);
  $( ".table tr:first-child td" ).addClass("bg-primary");
  $( ".table tr:first-child td a" ).addClass("text-light");
}

$(document).ready(() => {
  addPaginator();
})

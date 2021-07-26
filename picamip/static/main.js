/*
 * Python simple Raspberry-Pi camera module web interface
 * Copyright (C) 2021 Luiz Eduardo Amaral <luizamaral306@gmail.com>
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
    rows_per_page: 10,
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

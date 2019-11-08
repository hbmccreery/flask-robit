// var pitching_json = JSON.parse({{pit_rats|tojson}})
// var batting_json = JSON.parse({{bat_rats|tojson}})
// var other_json = JSON.parse({{other_rats|tojson}})
// var def_json = JSON.parse({{def_rats|tojson}})

// function fillColor(rat){
//     if (rat > 70){
//         return '#44bbdd';
//     }
//     else if (rat > 55){
//         return '#117722';
//     }
//     else if (rat > 40){
//         return '#eac117';
//     }
//     else if (rat > 25){
//         return '#dd8033';
//     }
//     else {
//         return '#dd0000';
//     }
// }

// width = 400;
// height = 200;
// left_margin = 50;
// bar_sep = 5;
// bar_width = 30;

function createRatingBars(svg, ratings){
    var bar_backgrounds = svg.selectAll('rect.backgrounds')
                            .data(ratings)
                            .enter()
                            .append('rect');

    bar_backgrounds.attr('height', bar_width)
                   .attr('width', function(d){return 240;})
                   .attr('x', left_margin)
                   .attr('y', function(d, i){return i*(bar_width + bar_sep);})
                   .attr('fill', 'lightgray');

    var pot_bars = svg.selectAll('rect.potentials')
                      .data(ratings)
                      .enter()
                      .append('rect');

    pot_bars.attr('height', bar_width)
            .attr('width', function(d){return 3*d['potential'];})
            .attr('x', left_margin)
            .attr('y', function(d, i){return i*(bar_width + bar_sep);})
            .attr('fill', function(d){return fillColor(d['potential']);})
            .attr('stroke', 'black')
            .style('opacity', 0.6);

    var cur_bars = svg.selectAll('rect.currents')
                      .data(ratings)
                      .enter()
                      .append('rect');

    cur_bars.attr('height', bar_width)
            .attr('width', function(d){return 3*d['current'];})
            .attr('x', left_margin)
            .attr('y', function(d, i){return i*(bar_width + bar_sep);})
            .attr('fill', function(d){return fillColor(d['current']);})
            .attr('stroke', 'black')
            .attr('stroke-width', 2);

    var cur_bar_labs = svg.selectAll('text.indexs')
                          .data(ratings)
                          .enter()
                          .append('text');

    cur_bar_labs.text(function(d){return d['index'];})
                .attr('x', 0)
                .attr('y', function(d, i){return (i+0.6)*(bar_width + bar_sep);});

    var cur_bar_values = svg.selectAll('text.currents')
                            .data(ratings)
                            .enter()
                            .append('text')

    cur_bar_values.text(function(d){return d['current'];})
                  .attr('x', left_margin + 250)
                  .attr('y', function(d, i){return (i+0.6)*(bar_width + bar_sep);})
                  .attr('fill', function(d){return fillColor(d['current'])});      

    var pot_bar_values = svg.selectAll('text.potentials')
                            .data(ratings)
                            .enter()
                            .append('text')

    pot_bar_values.text(function(d){return '/' + d['potential'];})
                  .attr('x', left_margin + 270)
                  .attr('y', function(d, i){return (i+0.6)*(bar_width + bar_sep);})
                  .attr('fill', function(d){return fillColor(d['potential'])}); 
}

// var selected_div = d3.select('#ratings')

// var bat_svg = selected_div.append('div')
//                 .attr('class', 'col-md-auto')
//                 .append('svg')
//                 .attr('width', width)
//                 .attr('height', height);

// createRatingBars(bat_svg, batting_json);

// var pit_svg = selected_div.append('div')
//                 .attr('class', 'col-md-auto')
//                 .append('svg')
//                 .attr('width', width)
//                 .attr('height', height);

// createRatingBars(pit_svg, pitching_json)

// var other_svg = selected_div.append('div')
//                 .attr('class', 'col-md-auto')
//                 .append('svg')
//                 .attr('width', width)
//                 .attr('height', height);

// createRatingBars(other_svg, other_json)

// def_height = 275

// var def_svg = selected_div.append('div')
//               .attr('class', 'col-md-auto')
//               .append('svg')
//               .attr('width', width)
//               .attr('height', def_height);

// createRatingBars(def_svg, def_json)

/* START */

const onTransitionStart = () => {
    // TODO reset all game variables
    resetNavbar();
    resetSubmit();
    resetVote();
    resetWinner();
};


const resetNavbar = () => {
    $navbarTimer.html("");
    navbarTimerSeconds = -1;
};


const resetSubmit = () => {
    // Text box
    $gameSubmitInput.prop('disabled', false);
    $gameSubmitInput.val("");

    // Send button
    $gameSubmitSend.removeClass('disabled');
    $gameSubmitSend.attr('data-badge', "0");

    // Skip button
    $gameSubmitSkip.removeClass('disabled');
    $gameSubmitSkip.attr('data-badge', "0");

    // Image
    $gameSubmitImageContainer.html("");
    gameCurrentImage = "";
};

const resetVote = () => {
    // TODO
    $gameVoteImageContainer.html("");
};

const resetWinner = () => {
    // TODO
    $gameWinnerImageContainer.html("");
};


/* VOTE */

const onTransitionVote = (subs) => {
    if(gameCurrentImage)
        $gameVoteImageContainer.html(
            $('<img>',{
                class: 'img-responsive',
                src: gameCurrentImage,
                width: '100%'
            })
        );
    else
        $gameVoteImageContainer.html("");
    /*
    for(let i = 0; i < subs.length; i++) {
        if(subs[i].name !== username)
            addVoteCard(i, subs[i].text);
    }
    */ // todo
};


/* WINNER */

const onTransitionWinner = (winners) => {
    for(let i = 0; i < winners.length; i++)
        addWinnerCard(winners[i].name, winners[i].text, winners[i].reacts);
};























// Sends a chat message
const sendUserSubmission = () => {
    if(!username) return;

    let text = cleanInput($gameSubmitInput.val().trim());

    if (text && auth) {
        socket.emit(USER_SUBMISSION, {
            username: username,
            text: text
        });
    }
};

const setGameImage = () => {
    if(gameCurrentImage)
        $gameSubmitImageContainer.html(
            $('<img>',{
                class: 'img-responsive',
                src: gameCurrentImage,
                width: '100%'
            })
        );
    else
        $gameSubmitImageContainer.html("");
};




const addWinnerCard = (name, title, reacts) => {
    $gameWinnerImageContainer.append(
        $('<div>', {
            class: 'column col-4 col-xl-12 memecard winner'
        }).html(
            $('<div>', {
                class: 'card shadow'
            }).html(
                $('<div>', {
                    class: 'card-header'
                }).html(
                    $('<div>', {
                        class: 'card-title h3 text'
                    }).html(title)
                )
            ).append(
                $('<div>', {
                    class: 'card-image image'
                }).html(
                    $('<img>',{
                        class: 'img-responsive',
                        src: gameCurrentImage,
                        width: '100%'
                    })
                )
            ).append(
                $('<div>', {
                    class: 'card-footer memereact-container'
                }).html(
                    $('<table>').html(
                        $('<tr>').html(
                            $('<td>').html(
                                $('<button>', {class: 'btn btn-link memereact winner unclickable'}).html('😍')
                            )
                        ).append(
                            $('<td>').html(
                                $('<button>', {class: 'btn btn-link memereact winner unclickable'}).html('😆')
                            )
                        ).append(
                            $('<td>').html(
                                $('<button>', {class: 'btn btn-link memereact winner unclickable'}).html('😮')
                            )
                        ).append(
                            $('<td>').html(
                                $('<button>', {class: 'btn btn-link memereact winner unclickable'}).html('😢')
                            )
                        ).append($('<td>').html(
                            $('<td>').html(
                                $('<button>', {class: 'btn btn-link memereact winner unclickable'}).html('😠')
                            )
                        ))
                    ).append(
                        $('<tr>', { class: 'react-count' }).html(
                            $('<td>').html($('<p>').html(reacts.love))
                        ).append(
                            $('<td>').html($('<p>').html(reacts.funny))
                        ).append(
                            $('<td>').html($('<p>').html(reacts.shock))
                        ).append(
                            $('<td>').html($('<p>').html(reacts.sad))
                        ).append(
                            $('<td>').html($('<p>').html(reacts.angry))
                        )
                    )

                ).append($('<div>', {class: 'winner'}).html(
                    $('<p>', {
                        class: 'name'
                    }).html(name)
                ))
            )
        )
    );
};



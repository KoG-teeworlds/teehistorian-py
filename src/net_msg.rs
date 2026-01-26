pub use libtw2_gamenet_ddnet::msg::game::Game as DdnetGameMsg;
use libtw2_gamenet_teeworlds_0_7::msg::Game;
pub use libtw2_gamenet_teeworlds_0_7::msg::game::Game as Tw07GameMsg;
use libtw2_packer::Unpacker;
use std::fmt;
use warn::Warn;

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub enum NetVersion {
    V06,
    V07,
    Unknown,
}

pub enum Error<'a> {
    NonClientGameMsg06(DdnetGameMsg<'a>),
    NonClientGameMsg07(Tw07GameMsg<'a>),
    NetMsgParseError(libtw2_gamenet_ddnet::error::Error),
}

impl fmt::Display for Error<'_> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        use Error::*;
        match self {
            NonClientGameMsg06(msg) => write!(f, "NonClientGameMsg06 {msg:?}"),
            NonClientGameMsg07(msg) => write!(f, "NonClientGameMsg07 {msg:?}"),
            NetMsgParseError(err) => write!(f, "NetMsgParseError {err:?}"),
        }
    }
}

#[derive(Debug)]
pub enum Chat {
    None,
    All,
    Team,
    Whisper,
}

impl From<libtw2_gamenet_teeworlds_0_7::enums::Chat> for Chat {
    fn from(chat: libtw2_gamenet_teeworlds_0_7::enums::Chat) -> Chat {
        use Chat::*;
        match chat {
            libtw2_gamenet_teeworlds_0_7::enums::Chat::None => None,
            libtw2_gamenet_teeworlds_0_7::enums::Chat::All => All,
            libtw2_gamenet_teeworlds_0_7::enums::Chat::Team => Team,
            libtw2_gamenet_teeworlds_0_7::enums::Chat::Whisper => Whisper,
        }
    }
}

pub struct ClSay<'a> {
    pub mode: Chat,
    pub target: i32,
    pub message: &'a [u8],
}

impl<'a> From<libtw2_gamenet_ddnet::msg::game::ClSay<'a>> for ClSay<'a> {
    fn from(cl_say: libtw2_gamenet_ddnet::msg::game::ClSay<'a>) -> ClSay<'a> {
        ClSay {
            mode: if cl_say.team { Chat::Team } else { Chat::All },
            target: -1,
            message: cl_say.message,
        }
    }
}

impl<'a> From<libtw2_gamenet_teeworlds_0_7::msg::game::ClSay<'a>> for ClSay<'a> {
    fn from(cl_say: libtw2_gamenet_teeworlds_0_7::msg::game::ClSay<'a>) -> ClSay<'a> {
        ClSay {
            mode: cl_say.mode.into(),
            target: cl_say.target,
            message: cl_say.message,
        }
    }
}

#[derive(Debug)]
pub enum Team {
    Spectators = -1,
    Red,
    Blue,
}

impl From<libtw2_gamenet_ddnet::enums::Team> for Team {
    fn from(team: libtw2_gamenet_ddnet::enums::Team) -> Team {
        use Team::*;
        match team {
            libtw2_gamenet_ddnet::enums::Team::Spectators => Spectators,
            libtw2_gamenet_ddnet::enums::Team::Red => Red,
            libtw2_gamenet_ddnet::enums::Team::Blue => Blue,
        }
    }
}

impl From<libtw2_gamenet_teeworlds_0_7::enums::Team> for Team {
    fn from(team: libtw2_gamenet_teeworlds_0_7::enums::Team) -> Team {
        use Team::*;
        match team {
            libtw2_gamenet_teeworlds_0_7::enums::Team::Spectators => Spectators,
            libtw2_gamenet_teeworlds_0_7::enums::Team::Red => Red,
            libtw2_gamenet_teeworlds_0_7::enums::Team::Blue => Blue,
        }
    }
}

#[derive(Debug)]
pub enum Spec {
    Freeview,
    Player,
    Flagred,
    Flagblue,
}

impl From<libtw2_gamenet_teeworlds_0_7::enums::Spec> for Spec {
    fn from(spec: libtw2_gamenet_teeworlds_0_7::enums::Spec) -> Spec {
        use Spec::*;
        match spec {
            libtw2_gamenet_teeworlds_0_7::enums::Spec::Freeview => Freeview,
            libtw2_gamenet_teeworlds_0_7::enums::Spec::Player => Player,
            libtw2_gamenet_teeworlds_0_7::enums::Spec::Flagred => Flagred,
            libtw2_gamenet_teeworlds_0_7::enums::Spec::Flagblue => Flagblue,
        }
    }
}

pub struct ClSetSpectatorMode {
    pub spec_mode: Spec,
    pub spectator_id: i32,
}

impl From<libtw2_gamenet_ddnet::msg::game::ClSetSpectatorMode> for ClSetSpectatorMode {
    fn from(
        cl_set_spectator_mode: libtw2_gamenet_ddnet::msg::game::ClSetSpectatorMode,
    ) -> ClSetSpectatorMode {
        ClSetSpectatorMode {
            spec_mode: if cl_set_spectator_mode.spectator_id == -1 {
                Spec::Freeview
            } else {
                Spec::Player
            },
            spectator_id: cl_set_spectator_mode.spectator_id,
        }
    }
}

impl From<libtw2_gamenet_teeworlds_0_7::msg::game::ClSetSpectatorMode> for ClSetSpectatorMode {
    fn from(
        cl_set_spectator_mode: libtw2_gamenet_teeworlds_0_7::msg::game::ClSetSpectatorMode,
    ) -> ClSetSpectatorMode {
        ClSetSpectatorMode {
            spec_mode: cl_set_spectator_mode.spec_mode.into(),
            spectator_id: cl_set_spectator_mode.spectator_id,
        }
    }
}

#[repr(i32)]
#[derive(Clone, Copy, Debug, PartialEq, PartialOrd, Eq, Hash, Ord)]
pub enum Emoticon {
    Oop,
    Exclamation,
    Hearts,
    Drop,
    Dotdot,
    Music,
    Sorry,
    Ghost,
    Sushi,
    Splattee,
    Deviltee,
    Zomg,
    Zzz,
    Wtf,
    Eyes,
    Question,
}

impl From<libtw2_gamenet_ddnet::enums::Emoticon> for Emoticon {
    fn from(emoticon: libtw2_gamenet_ddnet::enums::Emoticon) -> Emoticon {
        use Emoticon::*;
        match emoticon {
            libtw2_gamenet_ddnet::enums::Emoticon::Oop => Oop,
            libtw2_gamenet_ddnet::enums::Emoticon::Exclamation => Exclamation,
            libtw2_gamenet_ddnet::enums::Emoticon::Hearts => Hearts,
            libtw2_gamenet_ddnet::enums::Emoticon::Drop => Drop,
            libtw2_gamenet_ddnet::enums::Emoticon::Dotdot => Dotdot,
            libtw2_gamenet_ddnet::enums::Emoticon::Music => Music,
            libtw2_gamenet_ddnet::enums::Emoticon::Sorry => Sorry,
            libtw2_gamenet_ddnet::enums::Emoticon::Ghost => Ghost,
            libtw2_gamenet_ddnet::enums::Emoticon::Sushi => Sushi,
            libtw2_gamenet_ddnet::enums::Emoticon::Splattee => Splattee,
            libtw2_gamenet_ddnet::enums::Emoticon::Deviltee => Deviltee,
            libtw2_gamenet_ddnet::enums::Emoticon::Zomg => Zomg,
            libtw2_gamenet_ddnet::enums::Emoticon::Zzz => Zzz,
            libtw2_gamenet_ddnet::enums::Emoticon::Wtf => Wtf,
            libtw2_gamenet_ddnet::enums::Emoticon::Eyes => Eyes,
            libtw2_gamenet_ddnet::enums::Emoticon::Question => Question,
        }
    }
}

impl From<libtw2_gamenet_teeworlds_0_7::enums::Emoticon> for Emoticon {
    fn from(emoticon: libtw2_gamenet_teeworlds_0_7::enums::Emoticon) -> Emoticon {
        use Emoticon::*;
        match emoticon {
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Oop => Oop,
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Exclamation => Exclamation,
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Hearts => Hearts,
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Drop => Drop,
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Dotdot => Dotdot,
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Music => Music,
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Sorry => Sorry,
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Ghost => Ghost,
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Sushi => Sushi,
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Splattee => Splattee,
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Deviltee => Deviltee,
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Zomg => Zomg,
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Zzz => Zzz,
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Wtf => Wtf,
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Eyes => Eyes,
            libtw2_gamenet_teeworlds_0_7::enums::Emoticon::Question => Question,
        }
    }
}

pub struct ClCallVote<'a> {
    pub type_: &'a [u8],
    pub value: &'a [u8],
    pub reason: &'a [u8],
    pub force: bool,
}

impl<'a> From<libtw2_gamenet_ddnet::msg::game::ClCallVote<'a>> for ClCallVote<'a> {
    fn from(cl_call_vote: libtw2_gamenet_ddnet::msg::game::ClCallVote<'a>) -> ClCallVote<'a> {
        ClCallVote {
            type_: cl_call_vote.type_,
            value: cl_call_vote.value,
            reason: cl_call_vote.reason,
            force: false,
        }
    }
}

impl<'a> From<libtw2_gamenet_teeworlds_0_7::msg::game::ClCallVote<'a>> for ClCallVote<'a> {
    fn from(
        cl_call_vote: libtw2_gamenet_teeworlds_0_7::msg::game::ClCallVote<'a>,
    ) -> ClCallVote<'a> {
        ClCallVote {
            type_: cl_call_vote.type_,
            value: cl_call_vote.value,
            reason: cl_call_vote.reason,
            force: cl_call_vote.force,
        }
    }
}

pub struct Skin06<'a> {
    pub skin: &'a [u8],
    pub use_custom_color: bool,
    pub color_body: i32,
    pub color_feet: i32,
}

pub struct Skin07<'a> {
    pub skin_part_names: [&'a [u8]; 6],
    pub use_custom_colors: [bool; 6],
    pub skin_part_colors: [i32; 6],
}

pub enum Skin<'a> {
    V6(Skin06<'a>),
    V7(Skin07<'a>),
}

impl fmt::Display for Skin<'_> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Skin::V6(v6) => {
                let Skin06 {
                    skin,
                    use_custom_color,
                    color_body,
                    color_feet,
                } = v6;
                let skin = String::from_utf8_lossy(skin);
                write!(
                    f,
                    "{{ skin={skin:?} use_custom_color={use_custom_color} color_body={color_body} color_feet={color_feet} }}"
                )
            }
            Skin::V7(v7) => {
                let Skin07 {
                    skin_part_names,
                    use_custom_colors,
                    skin_part_colors,
                } = v7;
                write!(f, "{{")?;
                for i in 0..6 {
                    let name = String::from_utf8_lossy(skin_part_names[i]);
                    let custom = use_custom_colors[i];
                    let color = skin_part_colors[i];
                    write!(f, "(part={name} use_custom_color={custom} color={color})")?;
                    if i != 5 {
                        write!(f, " ")?;
                    }
                }
                write!(f, "}}")
            }
        }
    }
}

pub struct ClPlayerInfo<'a> {
    pub name: &'a [u8],
    pub clan: &'a [u8],
    pub country: i32,
    pub skin: Skin<'a>,
}

impl<'a> From<libtw2_gamenet_ddnet::msg::game::ClStartInfo<'a>> for ClPlayerInfo<'a> {
    fn from(cl_start_info: libtw2_gamenet_ddnet::msg::game::ClStartInfo<'a>) -> ClPlayerInfo<'a> {
        ClPlayerInfo {
            name: cl_start_info.name,
            clan: cl_start_info.clan,
            country: cl_start_info.country,
            skin: Skin::V6(Skin06 {
                skin: cl_start_info.skin,
                use_custom_color: cl_start_info.use_custom_color,
                color_body: cl_start_info.color_body,
                color_feet: cl_start_info.color_feet,
            }),
        }
    }
}

impl<'a> From<libtw2_gamenet_ddnet::msg::game::ClChangeInfo<'a>> for ClPlayerInfo<'a> {
    fn from(cl_change_info: libtw2_gamenet_ddnet::msg::game::ClChangeInfo<'a>) -> ClPlayerInfo<'a> {
        ClPlayerInfo {
            name: cl_change_info.name,
            clan: cl_change_info.clan,
            country: cl_change_info.country,
            skin: Skin::V6(Skin06 {
                skin: cl_change_info.skin,
                use_custom_color: cl_change_info.use_custom_color,
                color_body: cl_change_info.color_body,
                color_feet: cl_change_info.color_feet,
            }),
        }
    }
}

impl<'a> From<libtw2_gamenet_teeworlds_0_7::msg::game::ClStartInfo<'a>> for ClPlayerInfo<'a> {
    fn from(
        cl_start_info: libtw2_gamenet_teeworlds_0_7::msg::game::ClStartInfo<'a>,
    ) -> ClPlayerInfo<'a> {
        ClPlayerInfo {
            name: cl_start_info.name,
            clan: cl_start_info.clan,
            country: cl_start_info.country,
            skin: Skin::V7(Skin07 {
                skin_part_names: cl_start_info.skin_part_names,
                use_custom_colors: cl_start_info.use_custom_colors,
                skin_part_colors: cl_start_info.skin_part_colors,
            }),
        }
    }
}

pub struct ClShowDistance {
    pub x: i32,
    pub y: i32,
}

impl From<libtw2_gamenet_ddnet::msg::game::ClShowDistance> for ClShowDistance {
    fn from(cl_show_distance: libtw2_gamenet_ddnet::msg::game::ClShowDistance) -> ClShowDistance {
        ClShowDistance {
            x: cl_show_distance.x,
            y: cl_show_distance.y,
        }
    }
}

pub struct ClCommand<'a> {
    pub name: &'a [u8],
    pub arguments: &'a [u8],
}

impl<'a> From<libtw2_gamenet_teeworlds_0_7::msg::game::ClCommand<'a>> for ClCommand<'a> {
    fn from(cl_command: libtw2_gamenet_teeworlds_0_7::msg::game::ClCommand<'a>) -> ClCommand<'a> {
        ClCommand {
            name: cl_command.name,
            arguments: cl_command.arguments,
        }
    }
}

#[derive(Debug, Copy, Clone)]
pub struct ClReadyChange;

impl From<libtw2_gamenet_teeworlds_0_7::msg::game::ClReadyChange> for ClReadyChange {
    fn from(_: libtw2_gamenet_teeworlds_0_7::msg::game::ClReadyChange) -> ClReadyChange {
        ClReadyChange
    }
}

pub struct ClSkinChange<'a> {
    pub skin_part_names: [&'a [u8]; 6],
    pub use_custom_colors: [bool; 6],
    pub skin_part_colors: [i32; 6],
}

impl<'a> From<libtw2_gamenet_teeworlds_0_7::msg::game::ClSkinChange<'a>> for ClSkinChange<'a> {
    fn from(
        cl_skin_change: libtw2_gamenet_teeworlds_0_7::msg::game::ClSkinChange<'a>,
    ) -> ClSkinChange<'a> {
        ClSkinChange {
            skin_part_names: cl_skin_change.skin_part_names,
            use_custom_colors: cl_skin_change.use_custom_colors,
            skin_part_colors: cl_skin_change.skin_part_colors,
        }
    }
}

pub enum ClNetMessage<'a> {
    ClSay(ClSay<'a>),
    ClSetTeam(Team),
    ClSetSpectatorMode(ClSetSpectatorMode),
    ClStartInfo(ClPlayerInfo<'a>),
    ClChangeInfo(ClPlayerInfo<'a>),
    ClKill,
    ClEmoticon(Emoticon),
    ClVote(i32),
    ClCallVote(ClCallVote<'a>),
    /// contains the ddnet version
    ClIsDdnet(i32),
    ClShowOthers(i32),
    ClShowDistance(ClShowDistance),
    ClCommand(ClCommand<'a>),
    ClReadyChange(ClReadyChange),
    ClSkinChange(ClSkinChange<'a>),
}

// copied from https://github.com/heinrich5991/libtw2/blob/2872de4573e65d1690f1a5f344311df86d554eb4/tools/src/warn_stdout.rs
pub struct Stdout;
impl<W: fmt::Debug> Warn<W> for Stdout {
    fn warn(&mut self, warning: W) {
        println!("WARN: {warning:?}");
    }
}

#[allow(clippy::result_large_err)]
fn parse_ddnet(buf: &[u8]) -> Result<ClNetMessage, Error> {
    let mut b = Unpacker::new(buf);
    match DdnetGameMsg::decode(&mut Stdout, &mut b) {
        Ok(msg) => match msg {
            DdnetGameMsg::SvMotd(_)
            | DdnetGameMsg::SvBroadcast(_)
            | DdnetGameMsg::SvChat(_)
            | DdnetGameMsg::SvKillMsg(_)
            | DdnetGameMsg::SvKillMsgTeam(_)
            | DdnetGameMsg::SvSoundGlobal(_)
            | DdnetGameMsg::SvTuneParams(_)
            | DdnetGameMsg::SvReadyToEnter(_)
            | DdnetGameMsg::SvWeaponPickup(_)
            | DdnetGameMsg::SvEmoticon(_)
            | DdnetGameMsg::SvVoteClearOptions(_)
            | DdnetGameMsg::SvVoteOptionListAdd(_)
            | DdnetGameMsg::SvVoteOptionAdd(_)
            | DdnetGameMsg::SvVoteOptionRemove(_)
            | DdnetGameMsg::SvVoteSet(_)
            | DdnetGameMsg::SvVoteStatus(_)
            | DdnetGameMsg::SvDdraceTime(_)
            | DdnetGameMsg::SvRecord(_)
            | DdnetGameMsg::Unused(_)
            | DdnetGameMsg::Unused2(_)
            | DdnetGameMsg::SvTeamsState(_)
            | DdnetGameMsg::SvMyOwnMessage(_)
            | DdnetGameMsg::SvDdraceTimeLegacy(_)
            | DdnetGameMsg::SvRecordLegacy(_)
            | DdnetGameMsg::SvTeamsStateLegacy(_) => Err(Error::NonClientGameMsg06(msg)),
            DdnetGameMsg::ClSay(msg) => Ok(ClNetMessage::ClSay(msg.into())),
            DdnetGameMsg::ClSetTeam(msg) => Ok(ClNetMessage::ClSetTeam(msg.team.into())),
            DdnetGameMsg::ClSetSpectatorMode(msg) => {
                Ok(ClNetMessage::ClSetSpectatorMode(msg.into()))
            }
            DdnetGameMsg::ClStartInfo(msg) => Ok(ClNetMessage::ClStartInfo(msg.into())),
            DdnetGameMsg::ClChangeInfo(msg) => Ok(ClNetMessage::ClChangeInfo(msg.into())),
            DdnetGameMsg::ClKill(_) => Ok(ClNetMessage::ClKill),
            DdnetGameMsg::ClEmoticon(msg) => Ok(ClNetMessage::ClEmoticon(msg.emoticon.into())),
            DdnetGameMsg::ClVote(msg) => Ok(ClNetMessage::ClVote(msg.vote)),
            DdnetGameMsg::ClCallVote(msg) => Ok(ClNetMessage::ClCallVote(msg.into())),
            DdnetGameMsg::ClShowOthersLegacy(msg) => {
                Ok(ClNetMessage::ClShowOthers(msg.show as i32))
            }
            DdnetGameMsg::ClShowDistance(msg) => Ok(ClNetMessage::ClShowDistance(msg.into())),
            DdnetGameMsg::ClShowOthers(msg) => Ok(ClNetMessage::ClShowOthers(msg.show)),
            DdnetGameMsg::ClIsDdnetLegacy(_msg) => Ok(ClNetMessage::ClIsDdnet(0)),
        },
        Err(err) => Err(Error::NetMsgParseError(err)),
    }
}

#[allow(clippy::result_large_err)]
fn parse_teeworlds_07(buf: &[u8]) -> Result<ClNetMessage, Error> {
    let mut b = Unpacker::new(buf);
    match Tw07GameMsg::decode(&mut Stdout, &mut b) {
        Ok(msg) => match msg {
            Game::SvMotd(_)
            | Game::SvBroadcast(_)
            | Game::SvChat(_)
            | Game::SvTeam(_)
            | Game::SvKillMsg(_)
            | Game::SvTuneParams(_)
            | Game::SvExtraProjectile(_)
            | Game::SvReadyToEnter(_)
            | Game::SvWeaponPickup(_)
            | Game::SvEmoticon(_)
            | Game::SvVoteClearOptions(_)
            | Game::SvVoteOptionListAdd(_)
            | Game::SvVoteOptionAdd(_)
            | Game::SvVoteOptionRemove(_)
            | Game::SvVoteSet(_)
            | Game::SvVoteStatus(_)
            | Game::SvServerSettings(_)
            | Game::SvClientInfo(_)
            | Game::SvGameInfo(_)
            | Game::SvClientDrop(_)
            | Game::SvGameMsg(_)
            | Game::SvRaceFinish(_)
            | Game::SvCheckpoint(_)
            | Game::SvCommandInfo(_)
            | Game::SvCommandInfoRemove(_)
            | Game::SvSkinChange(_) => Err(Error::NonClientGameMsg07(msg)),
            Game::DeClientEnter(_) => Err(Error::NonClientGameMsg07(msg)),
            Game::DeClientLeave(_) => Err(Error::NonClientGameMsg07(msg)),
            Game::ClSay(msg) => Ok(ClNetMessage::ClSay(msg.into())),
            Game::ClSetTeam(msg) => Ok(ClNetMessage::ClSetTeam(msg.team.into())),
            Game::ClSetSpectatorMode(msg) => Ok(ClNetMessage::ClSetSpectatorMode(msg.into())),
            Game::ClStartInfo(msg) => Ok(ClNetMessage::ClStartInfo(msg.into())),
            Game::ClKill(_) => Ok(ClNetMessage::ClKill),
            Game::ClEmoticon(msg) => Ok(ClNetMessage::ClEmoticon(msg.emoticon.into())),
            Game::ClVote(msg) => Ok(ClNetMessage::ClVote(msg.vote)),
            Game::ClCallVote(msg) => Ok(ClNetMessage::ClCallVote(msg.into())),
            Game::ClSkinChange(msg) => Ok(ClNetMessage::ClSkinChange(msg.into())),
            Game::ClCommand(msg) => Ok(ClNetMessage::ClCommand(msg.into())),
            Game::ClReadyChange(msg) => Ok(ClNetMessage::ClReadyChange(msg.into())),
        },
        Err(err) => Err(Error::NetMsgParseError(err)),
    }
}

#[allow(clippy::result_large_err)]
pub fn parse_net_msg<'a>(
    buf: &'a [u8],
    net_version: &mut NetVersion,
) -> Result<ClNetMessage<'a>, Error<'a>> {
    match *net_version {
        NetVersion::V06 => parse_ddnet(buf),
        NetVersion::V07 => parse_teeworlds_07(buf),
        NetVersion::Unknown => match parse_ddnet(buf) {
            Ok(msg) => {
                *net_version = NetVersion::V06;
                Ok(msg)
            }
            Err(err) => {
                if let Ok(msg) = parse_teeworlds_07(buf) {
                    *net_version = NetVersion::V07;
                    Ok(msg)
                } else {
                    Err(err)
                }
            }
        },
    }
}

/// Encode player info back into a ClStartInfo or ClChangeInfo network message
/// Uses DDNet (0.6) protocol format with the libtw2 library's encoder
pub fn encode_player_info_message(
    message_type: &str,
    name: &str,
    clan: &str,
    country: i32,
    skin: &str,
    use_custom_color: bool,
    color_body: i32,
    color_feet: i32,
) -> Vec<u8> {
    // Use the library's proper encoding instead of manual packing
    // This ensures we use the correct wire format message IDs and encoding

    // Wrap in the appropriate Game enum variant
    let game_msg = if message_type == "ClStartInfo" {
        let player_info = libtw2_gamenet_ddnet::msg::game::ClStartInfo {
            name: name.as_bytes(),
            clan: clan.as_bytes(),
            country,
            skin: skin.as_bytes(),
            use_custom_color,
            color_body,
            color_feet,
        };
        libtw2_gamenet_ddnet::msg::game::Game::ClStartInfo(player_info)
    } else {
        let player_info = libtw2_gamenet_ddnet::msg::game::ClChangeInfo {
            name: name.as_bytes(),
            clan: clan.as_bytes(),
            country,
            skin: skin.as_bytes(),
            use_custom_color,
            color_body,
            color_feet,
        };
        libtw2_gamenet_ddnet::msg::game::Game::ClChangeInfo(player_info)
    };

    // Encode using the library's encoder
    let mut buf: Vec<u8> = Vec::with_capacity(256);
    {
        use libtw2_packer::with_packer;
        with_packer(&mut buf, |p| {
            // Let the library handle the encoding with correct message IDs
            let _ = game_msg.encode(p);
        });
    }

    buf
}

// Test function to check if libtw2 has encode capability
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_libtw2_encode_exists() {
        // Create a ClStartInfo message using the library's types
        let start_info = libtw2_gamenet_ddnet::msg::game::ClStartInfo {
            name: b"test",
            clan: b"",
            country: -1,
            skin: b"default",
            use_custom_color: false,
            color_body: 0,
            color_feet: 0,
        };

        // Wrap in Game enum
        let game_msg = libtw2_gamenet_ddnet::msg::game::Game::ClStartInfo(start_info);

        // Encode using the library's encoder
        let mut buf = Vec::new();
        {
            use libtw2_packer::with_packer;
            with_packer(&mut buf, |p| {
                // Call encode - pass Packer by value (it's Copy)
                game_msg.encode(p);
            });
        }

        println!("Encoded bytes (hex): {:02x?}", buf);
        println!("Length: {}", buf.len());

        // The encoded bytes should start with the message ID
        assert!(!buf.is_empty());
    }
}

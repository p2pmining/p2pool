CREATE TABLE IF NOT EXISTS `found_blocks` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `userid` varchar(36) NOT NULL,
  `block_hash` varchar(64) NOT NULL,
  `on_time` tinyint(1) NOT NULL,
  `timestamp` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `share_hash` (`block_hash`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

CREATE TABLE IF NOT EXISTS `live_shares` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `userid` varchar(36) NOT NULL,
  `shares` bigint(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `userid` (`userid`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

CREATE TABLE IF NOT EXISTS `miner_credits` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `rewardid` bigint(20) NOT NULL,
  `shiftid` bigint(20) NOT NULL,
  `shift_dataid` bigint(20) NOT NULL,
  `value` decimal(16,8) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `currency` varchar(3) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

CREATE TABLE IF NOT EXISTS `p2pool_shares` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `userid` varchar(36) NOT NULL,
  `share_hash` varchar(8) NOT NULL,
  `on_time` tinyint(1) NOT NULL,
  `timestamp` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `share_hash` (`share_hash`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

CREATE TABLE IF NOT EXISTS `pool_earnings` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `timestamp` int(11) NOT NULL,
  `miner_credits_id` bigint(20) NOT NULL,
  `fee` decimal(16,8) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

CREATE TABLE IF NOT EXISTS `pool_rewards_main` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `blockhash` varchar(64) NOT NULL,
  `txid` varchar(64) NOT NULL DEFAULT 'NONE',
  `value` decimal(16,8) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `confirmations` int(11) NOT NULL,
  `orphan` tinyint(1) NOT NULL DEFAULT '0',
  `distributed` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `blockhash` (`blockhash`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

CREATE TABLE IF NOT EXISTS `shifts` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `timestamp` bigint(20) NOT NULL,
  `shiftpay` decimal(16,8) NOT NULL,
  `lastblockheight` bigint(20) NOT NULL,
  `confirmed` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

CREATE TABLE IF NOT EXISTS `shift_data` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `userid` varchar(36) NOT NULL,
  `shares` bigint(20) NOT NULL,
  `shiftid` bigint(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;